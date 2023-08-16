ReAct_Prompt = """Using the ReAct framework, please provide reasoning traces and task-specific actions when answering the following question. Your only action is 'SearchKB' (Search Knowledge Base). Given this constraint, answer the question provided by the user in single backticks.
There can be Thought, Action, Observation or FinalAnswer available after the question. So please do not to repeat a same Thought or Observation. Do not repeat the same search text for the action. If the latest search didn't extract any answer, try to change the search text.
If you don't get any answer from any of the Action try to divide what you are searching. Sometimes information about what you are trying to search might not be available together. You might need to go more granular.
If you don't know how ReAct framework works, refer the following example.
Question: `What is the elevation range for the area that the eastern sector of the Colorado orogeny extends into?`
Thought: I need to search Colorado orogeny, find the area that the eastern sector of the Colorado orogeny extends into, then find the elevation range of the area.
Action: SearchKB with argument search_text: "Colorado orogeny"
Observation: The Colorado orogeny was an episode of mountain building (an orogeny) in Colorado and surrounding areas.
Thought: It does not mention the eastern sector. So I need to look up eastern sector.
Action: SearchKB with argument search_text: "Colorado orogeny eastern sector"
Observation: The eastern sector extends into the High Plains and is called the Central Plains orogeny.
Thought: The eastern sector of Colorado orogeny extends into the High Plains. So I need to search High Plains and find its elevation range.
Action: SearchKB with argument search_text: "Colorado orogeny easter sector High Plains" Observation: The High Plains are a subregion of the Great Plains. From east to west, the High Plains rise in elevation from around 1,800 to 7,000 ft (550 to 2,130m)
Thought: High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer is 1,800 to 7,000 ft.
FinalAnswer: If the final answer can be reached.
The provided example is generic but you have to follow the steps as followed in the example.
First think, have a thought based on what's the question and then go take an action. Don't directly take any action without a thought in the history. Use the respective functions for Thought, Action, Observation, and FinalAnswer to reply.
A Thought is followed by an Action and an Action is followed by either Observation or FinalAnswer. I the final answer is not reached start with a Thought and follow the same process.
You have access to the history so don't repeat (call) the same Thoughts or Observations which are already available in the history. Also do not search the same search_text again if its already available in the history.
If you don't get any answer from the Action change the search_text in the next iteration.
Please go step by step, don't directly try and reach the final answer. Don't assume things!
"""

ReAct_Answer_Prompt = """You will be provided with a question inside single backticks and history of action and reasoning inside triple backticks. The history will contain a flow of Thought, Action, Answer (Search Result), and Observation in multiple numbers. Using the history you need to answer the provided question. You just need to use the history to answer, please don't use your knowledge to answer. Moreover, using the history provide an explanation for the answer you reached at."""