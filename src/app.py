import os
import yaml
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any
def load_config() -> Dict:
    """Load application configuration from YAML file"""
    with open("config.yaml") as f:
        return yaml.safe_load(f)


class LinkedInParser:
    def __init__(self, profile_path: str):
        self.profile_path = profile_path
        
    def parse_profile(self) -> Dict[str, Any]:
        """Parse LinkedIn profile JSON data"""
        with open(self.profile_path) as f:
            return json.load(f)

class ATSOptimizer:
    def __init__(self, config: Dict):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            http_client=httpx.Client(
                headers={
                    "HTTP-Referer": "https://github.com/ApplicantOptimizer",
                    "X-Title": "Applicant Optimizer"
                }
            )
        )
        self.analysis_config = config['resume_analysis']
        self.generation_config = config['resume_generation']
        
    def analyze_gaps(self, profile_data: Dict, job_desc: str) -> Dict:
        """LLM-powered gap analysis with concrete improvement suggestions"""
        system_msg = """You're an ATS optimization expert. Analyze the LinkedIn profile against 
        the job description. Identify missing hard skills, insufficient experience durations, 
        and keyword gaps. Format response with JSON containing: qualified(bool), 
        gap_analysis(list), improvement_plan(list), and ats_score(0-100)."""
        
        response = self.client.chat.completions.create(
            model=self.analysis_config['model'],
            messages=[{
                "role": "system",
                "content": system_msg
            }, {
                "role": "user",
                "content": f"PROFILE: {json.dumps(profile_data)}\n\nJOB DESC: {job_desc}"
            }],
            temperature=self.analysis_config['temperature'],
            max_tokens=self.analysis_config['max_tokens'],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

class DocumentGenerator:
    def generate_resume(self, profile_data: Dict, optimization_data: Dict) -> str:
        """Generate ATS-optimized resume incorporating gap analysis"""
        # Implementation would use template engine with LLM-enhanced content
        return "generated_resume.pdf"
    
    def generate_cover_letter(self, profile_data: Dict, job_desc: str) -> str:
        """Create targeted cover letter using LLM"""
        return "cover_letter.docx"
    
    def generate_improvement_plan(self, analysis: Dict) -> str:
        """Create actionable PDF improvement guide"""
        return "improvement_plan.pdf"

def main():
    # Initialize core components
    config = load_config()
    load_dotenv()
    
    # Process inputs
    parser = LinkedInParser("input/linkedin_profile.json")
    profile = parser.parse_profile()
    
    with open("input/job_description.txt") as f:
        job_desc = f.read()
    
    # Perform analysis
    optimizer = ATSOptimizer(config)
    analysis = optimizer.analyze_gaps(profile, job_desc)
    
    # Generate outputs
    generator = DocumentGenerator()
    if analysis['qualified']:
        generator.generate_resume(profile, analysis)
        generator.generate_cover_letter(profile, job_desc)
    else:
        generator.generate_improvement_plan(analysis)

if __name__ == "__main__":
    main()