import discord
from discord.ext import commands
from sympy.parsing.sympy_parser import parse_expr
from sympy.plotting import plot as sympy_plot
import re, os
from helper import generate_random_name

plot_re = re.compile(r"```(.+)```", flags=re.DOTALL)

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(20, 60, commands.BucketType.user)
    async def solve(self, ctx, *, equation):
        "Solve basic math problem."
        res = str(parse_expr(equation))
        await ctx.send(f"```{res}```")
    
    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def plot(self, ctx, *, equations):
        equations = plot_re.match(equations)
        if not equations:
            return await ctx.send("Please send valid equations inside a code block!")

        sympy_eqs = []
        for equation in equations.group(1).splitlines():
            if not equation.strip():
                continue
            parsed = parse_expr(equation)
            plot = sympy_plot(parsed, show=False)
            sympy_eqs.append(plot)
        
        if not sympy_eqs:
            return await ctx.send("Please send at least one equation!")
        
        base_plot = sympy_eqs[0]
        for plot in sympy_eqs:
            base_plot.extend(plot)
        
        plot_path = "tmp/plot-" + generate_random_name(10) + ".jpg"
        base_plot.save(plot_path)
        
        await ctx.send("Done!", file=discord.File(plot_path))

        try:
            os.remove(plot_path)
        except BaseException:
            pass
        
def setup(bot):
    bot.add_cog(Math(bot))