import os
import argparse
from time import sleep
from typing import List, Dict, Union

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

from config.config import *
from react.prompt import ReAct_Prompt, ReAct_Answer_Prompt
from react.schemas import Functions
from actions.search import SearchKnowledgeBase
from react.completion import NormalCompletion, TokenPadding, StreamCompletion
from react.func_call import FunctionCall


parser = argparse.ArgumentParser(description="Run the ReAct bot with custom settings.")

parser.add_argument(
    "--pinecone_index_name",
    default=None,
    help="Name of the Pinecone index. Default is None.",
)

parser.add_argument(
    "--pinecone_namespace",
    default=None,
    help="Name of the Pinecone namespace. Default is None.",
)

parser.add_argument(
    "--model_name",
    default="gpt-4",
    help="Name of the model to be used. Default is 'gpt-4'.",
)

args = parser.parse_args()


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


model_name = args.model_name
token_padding = TokenPadding(model_name)
complete = NormalCompletion(OPENAI_API_KEY)
stream_complete = StreamCompletion(OPENAI_API_KEY)
fc = FunctionCall(OPENAI_API_KEY)
search = SearchKnowledgeBase(
    PINECONE_API_KEY,
    PINECONE_ENV,
    args.pinecone_index_name,
    args.pinecone_namespace,
    complete,
    token_padding,
    model=model_name,
)

console = Console()


def log_function(function_name: str, function_arguments: Union[Dict, str]):
    mapping = {
        "Thought": lambda function_arguments: console.print(
            f'[bold green]Thought:[/bold green] [italic green]{function_arguments.get("thought_text")}[/italic green]'
        ),
        "Action": lambda function_arguments: console.print(
            f'[bold magenta]Action: {function_arguments.get("action_type")}[/bold magenta] => [underline]Search Text:[/underline] [italic magenta]{function_arguments.get("search_text")}[/italic magenta]'
        ),
        "Answer": lambda function_arguments: console.print(
            f"[bold blue]Answer: [/bold blue] [italic blue]{function_arguments}[/italic blue]"
        ),
        "Observation": lambda function_arguments: console.print(
            f"[bold cyan]Observation: [/bold cyan] [italic cyan]{function_arguments.get('observation_text')}[/italic cyan]"
        ),
        "FinalAnswer": lambda function_arguments: console.print(
            f"[bold green]Final Answer: [/bold green] [italic green]{function_arguments.get('reached_final_answer')}[/italic green]"
        )
        if function_arguments.get("reached_final_answer")
        else console.print(
            f"[bold red]Final Answer: [/bold red] [italic red]{function_arguments.get('reached_final_answer')}[/italic red]"
        ),
        "Exit": lambda function_arguments: console.print(
            f"[bold red]Exit: [/bold red] [red]{function_arguments.get('exit')}[/red]"
        ),
    }
    mapping[function_name](function_arguments)


def reAct(question: str):
    history = """"""
    history_calls = []

    def agent(
        question: Union[str, None],
        function_name: Union[str, None],
        function_arguments: Union[Dict, None],
        history: str = """""",
        false_counts: int = 0,
    ):
        if false_counts >= 4:
            return history, history_calls
        if question:
            history += f"Question: `{question}`"
            with Live(
                Spinner("dots", text="Thinking..."),
                refresh_per_second=10,
                transient=True,
            ):
                fn, fa = fc(history, ReAct_Prompt, Functions.functions, model_name)
            history_calls.append({"fn": fn, "fa": fa})
            # print(f"""Function: {fn} | Arguments: {fa}""")
            log_function(fn, fa)
            # print(f"History: {history}")
            return agent(None, fn, fa, history)
        else:
            if function_name == "Action":
                search_text = function_arguments.get("search_text")
                with Live(
                    Spinner("dots", text="Searching..."),
                    refresh_per_second=10,
                    transient=True,
                ):
                    answer = search(search_text)
                history += f"\nSearchKB with search_text '{search_text}'"
                history += f"\nSearch Result: {answer}"
                # print("Search Result: ", answer)
                # print(f"History: {history}")
                log_function("Answer", answer)
                with Live(
                    Spinner("dots", text="Thinking..."),
                    refresh_per_second=10,
                    transient=True,
                ):
                    fn, fa = fc(history, ReAct_Prompt, Functions.functions, model_name)
                # print(f"""Function: {fn} | Arguments: {fa}""")
                history_calls.append({"fn": fn, "fa": fa})
                log_function(fn, fa)
                return agent(None, fn, fa, history)
            elif function_name == "Thought":
                history += f"\nThought: {function_arguments.get('thought_text')}"
                # print(f"History: {history}")
                with Live(
                    Spinner("dots", text="Thinking..."),
                    refresh_per_second=10,
                    transient=True,
                ):
                    fn, fa = fc(history, ReAct_Prompt, Functions.functions, model_name)
                # print(f"""Function: {fn} | Arguments: {fa}""")
                history_calls.append({"fn": fn, "fa": fa})
                log_function(fn, fa)
                return agent(None, fn, fa, history)
            elif function_name == "Observation":
                history += f"""\nObservation: {function_arguments.get('observation_text')}
                """
                # print(f"History: {history}")
                with Live(
                    Spinner("dots", text="Thinking..."),
                    refresh_per_second=10,
                    transient=True,
                ):
                    fn, fa = fc(history, ReAct_Prompt, Functions.functions, model_name)
                # print(f"""Function: {fn} | Arguments: {fa}""")
                history_calls.append({"fn": fn, "fa": fa})
                log_function(fn, fa)
                return agent(None, fn, fa, history)
            elif function_name == "Exit":
                return history, history_calls
            elif function_name == "FinalAnswer":
                history += f"""\nFinal Answer: {function_arguments.get('reached_final_answer')}
                """
                # print(f"History: {history}")
                if function_arguments.get("reached_final_answer"):
                    print(f"Inside Final Answer Returning")
                    return history, history_calls
                else:
                    false_counts += 1
                    if false_counts > 4:
                        return history, history_calls
                    else:
                        with Live(
                            Spinner("dots", text="Thinking..."),
                            refresh_per_second=10,
                            transient=True,
                        ):
                            fn, fa = fc(
                                history,
                                ReAct_Prompt,
                                Functions.functions,
                                model_name,
                            )
                        history_calls.append({"fn": fn, "fa": fa})
                        log_function(fn, fa)
                        return agent(None, fn, fa, history, false_counts)
            else:
                print(f"ERROR: Called unavailable function. Terminating Agent!")
                return history, history_calls

    history, history_calls = agent(question, None, None, history)
    message = f"""Question: `{question}` History: ```{history}```
    """
    final_answer = ""
    for msg in stream_complete(message, ReAct_Answer_Prompt, model_name):
        final_answer += msg
        clear_terminal()
        print(final_answer, end="", flush=True)
        sleep(0.1)


if __name__ == "__main__":
    while True:
        question = input("\nEnter your question: ")
        question = question.rstrip().lstrip()
        if question:
            reAct(question)
        else:
            pass
