import discord
from discord.ext import commands
from sympy.parsing.sympy_parser import stringify_expr, eval_expr, parse_expr, standard_transformations, convert_xor, convert_equals_signs, implicit_multiplication, split_symbols, function_exponentiation, implicit_application
from sympy.plotting import plot as sympy_plot
import re, os
from helper import generate_random_name
from token import NAME
block_re = re.compile(r"```(.+)```", flags=re.DOTALL)

# START BLOCK
# From https://github.com/sympy/sympy_gamma/blob/master/app/logic/logic.py
PREEXEC = """from sympy import *
from sympy.solvers.diophantine import diophantine
"""

# From https://github.com/sympy/sympy_gamma/blob/master/app/logic/utils.py
SYNONYMS = {
    u'derivative': 'diff',
    u'derive': 'diff',
    u'integral': 'integrate',
    u'antiderivative': 'integrate',
    u'factorize': 'factor',
    u'graph': 'plot',
    u'draw': 'plot'
}

def synonyms(tokens, local_dict, global_dict):
    result = []
    for token in tokens:
        if token[0] == NAME:
            if token[1] in SYNONYMS:
                result.append((NAME, SYNONYMS[token[1]]))
                continue
        result.append(token)
    return result

def custom_implicit_transformation(result, local_dict, global_dict):
    for step in (split_symbols, implicit_multiplication,
                 implicit_application, function_exponentiation):
        result = step(result, local_dict, global_dict)

    return result
# END BLOCK

namespace = {}
for exec_str in PREEXEC.splitlines():
    exec(exec_str, {}, namespace)

def plot(*args):
    return "Please use `f!plot` instead."
namespace.update({
    'plot': plot
})

transforms = [
    convert_equals_signs,
    convert_xor,
    synonyms,
]
transforms.extend(standard_transformations)


class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(20, 60, commands.BucketType.user)
    async def solve(self, ctx, *, equations):
        """Solve basic math problem.
        
        If you want to do multiple equations, do it inside a code block, splitted by new lines."""
        show_help = False
        matches = block_re.match(equations)
        if matches:
            splitted_lines = list(filter(None, matches.group(1).splitlines()))
            if len(splitted_lines) > 5:
                return await ctx.send("Only 5 equations maximum is allowed.")
        else:
            splitted_lines = [equations]

        response = ""
        i = 1
        for equation in splitted_lines:
            if not equation.strip():
                continue
            response += f"\r{i}. "
            try:
                parsed = stringify_expr(equation, {}, namespace, transforms)
                evaluated = eval_expr(parsed, {}, namespace)
                response += repr(evaluated)
            except Exception as e:
                response += f"{e.__class__.__name__} occured."
            i += 1
        await ctx.send(f"```{response}```")
    
    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def plot(self, ctx, *, equations):
        """Draws plots of given equation.
        
        If you want to do multiple equations, do it inside a code block, splitted by new lines."""
        matches = block_re.match(equations)
        if matches:
            splitted_lines = list(
                filter(
                    lambda x: not (bool(x) or "help" in x),
                    matches.group(1).splitlines()
                )
            )
            if len(splitted_lines) > 5:
                return await ctx.send("Only 5 equations maximum is allowed.")
        else:
            splitted_lines = [equations]

        sympy_eqs = []
        for equation in splitted_lines:
            if not equation.strip():
                continue
            parsed = stringify_expr(equation, {}, namespace, transforms)
            evaluated = eval_expr(parsed, {}, namespace)
            e_plot = sympy_plot(evaluated, show=False)
            sympy_eqs.append(e_plot)
        
        if not sympy_eqs:
            return await ctx.send("Please send at least one equation!")
        
        base_plot = sympy_eqs[0]
        for e_plot in sympy_eqs:
            base_plot.extend(e_plot)
        
        plot_path = "tmp/plot-" + generate_random_name(10) + ".png"
        base_plot.save(plot_path)
        
        await ctx.send("Done!", file=discord.File(plot_path))

        try:
            os.remove(plot_path)
        except BaseException:
            pass
        
def setup(bot):
    bot.add_cog(Math(bot))