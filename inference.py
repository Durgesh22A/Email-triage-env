import os
import json
from openai import OpenAI
from environment import EmailTriageEnv

# ================================
# SETUP CLIENT
# ================================
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

# ================================
# ASK LLM
# ================================
def ask_agent(observation) -> dict:
    prompt = f"""You are an email triage assistant.
    
Observation Details:
{observation}

Classify this email by responding ONLY with valid JSON like this:
{{
  "priority": "urgent" or "normal" or "low",
  "category": "support" or "sales" or "spam" or "hr",
  "action": "reply" or "forward" or "archive" or "delete"
}}
Respond with JSON only. No explanation."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return None

# ================================
# RUN BENCHMARK
# ================================
def run_benchmark():
    tasks = ["task1_easy", "task2_medium", "task3_hard"]
    
    for task_name in tasks:
        env = EmailTriageEnv(task_name)
        obs_obj = env.reset()
        observation = obs_obj.model_dump()
        
        print(f"[START] task={task_name} env=email-triage model={MODEL_NAME}")
        
        step_count = 0
        rewards_history = []
        done = False
        success = False
        
        while not done:
            step_count += 1
            error_msg = "null"
            
            action_data = ask_agent(observation)
            
            if not action_data:
                error_msg = "llm_json_parse_error"
                action_data = {"priority": "normal", "category": "support", "action": "reply"}
            
            action_str = json.dumps(action_data).replace(" ", "")
            
            try:
                from environment import Action
                act_obj = Action(**action_data)
                obs_obj, reward_obj, done, info = env.step(act_obj)
                reward = reward_obj.score
                rewards_history.append(reward)
            except Exception as e:
                error_msg = str(e).replace("\n", " ").replace(",", ";")
                reward = 0.00
                rewards_history.append(reward)
                done = True
                
            formatted_reward = f"{float(reward):.2f}"
            formatted_done = str(done).lower()
            
            print(f"[STEP] step={step_count} action={action_str} reward={formatted_reward} done={formatted_done} error={error_msg}")
            
            if done:
                success = reward >= 1.0
                break

        formatted_success = str(success).lower()
        rewards_str = ",".join([f"{float(r):.2f}" for r in rewards_history])
        print(f"[END] success={formatted_success} steps={step_count} rewards={rewards_str}")

if __name__ == "__main__":
    run_benchmark()