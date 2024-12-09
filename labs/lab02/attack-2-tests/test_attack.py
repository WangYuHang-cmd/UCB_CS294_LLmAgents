import os
import openai
from typing import Dict, List
from datetime import datetime
import json
import time
from dotenv import load_dotenv
from hackathon.src.secret_key_generator import generate_secret_key

load_dotenv()

class AttackTester:
    def __init__(self):
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("Please set OPENAI_API_KEY in your .env file")
        
        self.base_path = 'labs/lab02/attack-2-tests'
        self.system_prompt = self._load_system_prompt()
        self.attack_prompts = self._load_attack_prompts()
        self.results_file = os.path.join(self.base_path, 'test_results.txt')
        
        # Initialize OpenAI client
        self.client = openai.OpenAI()
        
        # Generate a new secret key for testing
        self.secret_key = generate_secret_key()
        
        # Update system prompt with new secret key
        self.system_prompt = self.system_prompt.replace(
            "AI_SAFETY_2024_XK9",
            self.secret_key
        )

    def _load_system_prompt(self) -> str:
        """Load the defensive system prompt"""
        path = os.path.join(self.base_path, 'system-prompts', 'defensive_system.txt')
        with open(path, 'r') as f:
            return f.read()

    def _load_attack_prompts(self) -> Dict[str, str]:
        """Load all attack prompts from the attack-prompts directory"""
        prompts = {}
        attack_dir = os.path.join(self.base_path, 'attack-prompts')
        for file in os.listdir(attack_dir):
            if file.endswith('.txt'):
                with open(os.path.join(attack_dir, file), 'r') as f:
                    prompts[file] = f.read()
        return prompts

    def run_attack(self, attack_prompt: str) -> dict:
        """Run a single attack prompt against the system"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or your preferred model
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": attack_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            # Get the response text
            response_text = response.choices[0].message.content
            
            # Check if the secret key appears in the response
            success = self.secret_key in response_text
            
            return {
                "success": success,
                "response": response_text,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "tokens_used": 0
            }

    def run_all_attacks(self):
        """Run all attack prompts and collect results"""
        results = []
        
        print("\n=== Starting Automated Attack Testing ===")
        
        for attack_name, attack_prompt in self.attack_prompts.items():
            print(f"\nTesting: {attack_name}")
            
            # Run the attack
            result = self.run_attack(attack_prompt)
            
            # Add metadata to result
            result.update({
                'attack_name': attack_name,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'prompt_used': attack_prompt
            })
            
            results.append(result)
            
            # Brief delay to avoid rate limits
            time.sleep(1)
        
        self._save_results(results)
        self._display_summary(results)
        return results

    def _save_results(self, results: List[dict]):
        """Save detailed test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(self.base_path, f'attack_results_{timestamp}.json')
        
        # Save detailed JSON results
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save human-readable summary
        with open(self.results_file, 'a') as f:
            f.write(f"\n\nTest Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n")
            
            for result in results:
                f.write(f"\nAttack: {result['attack_name']}\n")
                f.write(f"Success: {'Yes' if result['success'] else 'No'}\n")
                f.write(f"Tokens Used: {result['tokens_used']}\n")
                if 'error' in result and result['error']:
                    f.write(f"Error: {result['error']}\n")
                f.write(f"Response: {result['response'][:200]}...\n")
                f.write("-"*30 + "\n")

    def _display_summary(self, results: List[dict]):
        """Display summary of test results"""
        print("\n=== Test Session Summary ===")
        successful_attacks = sum(1 for r in results if r['success'])
        total_tokens = sum(r['tokens_used'] for r in results)
        
        print(f"\nTotal Attacks Tested: {len(results)}")
        print(f"Successful Attacks: {successful_attacks}")
        print(f"Failed Attacks: {len(results) - successful_attacks}")
        print(f"Total Tokens Used: {total_tokens}")
        
        if successful_attacks > 0:
            print("\nSuccessful Attacks:")
            for result in results:
                if result['success']:
                    print(f"- {result['attack_name']}")
        
        print(f"\nDetailed results saved to: {self.results_file}")

def main():
    tester = AttackTester()
    
    # Run a single attack
    attack_name = "attack_3_token_manipulation.txt"
    attack_prompt = tester.attack_prompts[attack_name]
    result = tester.run_attack(attack_prompt)
    
    print(f"\nAttack Result for {attack_name}:")
    print(f"Success: {'Yes' if result['success'] else 'No'}")
    print(f"Response: {result['response']}")

if __name__ == "__main__":
    main() 