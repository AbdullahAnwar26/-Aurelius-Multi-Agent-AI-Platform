from AI.Agents.Qna_Agent.qna_agent import qna_agent_response

def handle_qna_agent(user_input, file_path=None):
    # This wraps the AI logic from the QnA agent
    response = qna_agent_response(user_input, file_path)
    return response
