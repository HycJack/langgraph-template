from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "")
)
def call_llm(sysPrompt, prompt):    
    model = os.environ.get("MODEL", "")
    # Make a streaming chat completion request
    r = client.chat.completions.create(
         model=model,
         messages=[
                {"role": "system", "content": sysPrompt},
                {"role": "user", "content": prompt}
            ],
    )
    return r.choices[0].message.content


if __name__ == "__main__":
    print("## Testing call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = call_llm('',prompt)
    print(f"## Response: {response}")
    
