import asyncio
import re
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from token import NAME

from discord.ext import commands
from sympy.parsing.sympy_parser import (
    convert_equals_signs, convert_xor, eval_expr, function_exponentiation,
    implicit_application, implicit_multiplication, split_symbols,
    standard_transformations, stringify_expr)

block_re = re.compile(r"```(.+)```", flags=re.DOTALL)

# START BLOCK
# From https://github.com/sympy/sympy_gamma/blob/master/app/logic/logic.py
PREEXEC = """from sympy import *
from sympy.solvers.diophantine import diophantine
"""

# From https://github.com/sympy/sympy_gamma/blob/master/app/logic/utils.py
SYNONYMS = {
    "derivative": "diff",
    "derive": "diff",
    "integral": "integrate",
    "antiderivative": "integrate",
    "factorize": "factor",
    "graph": "plot",
    "draw": "plot",
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
    for step in (
        split_symbols,
        implicit_multiplication,
        implicit_application,
        function_exponentiation,
    ):
        result = step(result, local_dict, global_dict)

    return result


# END BLOCK

namespace = {}
for exec_str in PREEXEC.splitlines():
    exec(exec_str, {}, namespace)


def plot(*args):
    return "Please use `f!plot` instead."


namespace.update({"plot": plot})

transforms = [
    convert_equals_signs,
    convert_xor,
    synonyms,
]
transforms.extend(standard_transformations)


class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thread_pool = ThreadPoolExecutor()

    def _do_equations(self, equations):
        response = ""
        i = 1
        for equation in equations:
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

    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def solve(self, ctx, *, equations):
        """Solve basic math problem.

        If you want to do multiple equations, do it inside a code block, splitted by new lines."""
        matches = block_re.match(equations)
        if matches:
            splitted_lines = list(filter(None, matches.group(1).splitlines()))
            if len(splitted_lines) > 5:
                return await ctx.send("Only 5 equations maximum is allowed.")
        else:
            splitted_lines = [equations]

        task = self.bot.loop.run_in_executor(
            self.thread_pool, partial(self._do_equations, splitted_lines)
        )
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            return await ctx.send("Command timeout.")

        if len(response) > 1994:
            return await ctx.send(
                "The result(s) requires more than 2000 characters. Aborting."
            )
        await ctx.send(f"```{response}```")


def setup(bot):
    bot.add_cog(Math(bot))
