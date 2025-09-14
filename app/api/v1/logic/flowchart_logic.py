from google import genai
import json
import os
from typing import Dict, Any, List, Optional
from app.models.BaseModel.flowchart import flowchart_response, Node, Nodes
from app.services.personalization.prompt_enhancer import enhance_prompt_with_personalization
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class FlowchartGenerator:
    def __init__(self):
        """Initialize the FlowchartGenerator with Gemini API configuration."""
        # Configure the Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # genai.configure(api_key=api_key)
        # self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _create_flowchart_prompt(self, text: str, instruction: Optional[str] = None, userId: Optional[str] = None, language: Optional[str] = "English") -> str:
        """Create a detailed prompt for flowchart generation."""
        
        # Base prompt
        base_prompt = f"""
        You are an expert at creating educational flowcharts. Based on the following text, create a hierarchical flowchart that represents the main concepts, processes, or relationships described.

        CRITICAL LANGUAGE REQUIREMENT: 
        - You MUST respond STRICTLY in {language} language ONLY
        - ALL content including title and node labels MUST be in {language}
        - Do NOT use any other language regardless of the input text language
        - If input text is in a different language, translate concepts to {language}
        - This is a MANDATORY requirement that cannot be ignored

        Text to analyze:
        {text}"""
        
        # Add user instruction if provided
        if instruction and instruction.strip():
            base_prompt += f"""
        
        Special Instructions:
        {instruction.strip()}
        
        Please follow these instructions carefully while creating the flowchart."""
        
        base_prompt += """

        Please generate a JSON response with the following exact structure:
        {{
            "title": "A clear, descriptive title for the flowchart (max 100 characters)",
            "flowchart": {{
                "nodes": [
                    {{
                        "label": "Main concept or step (clear and concise)",
                        "children": [1, 2]
                    }},
                    {{
                        "label": "Sub-concept 1",
                        "children": [3]
                    }},
                    {{
                        "label": "Sub-concept 2",
                        "children": null
                    }},
                    {{
                        "label": "Detailed point under sub-concept 1",
                        "children": null
                    }}
                ]
            }}
        }}

        Guidelines:
        1. Start with a main concept or process as the root node (index 0)
        2. Use children arrays with indices to reference other nodes in the list
        3. Set children to null for leaf nodes (no further breakdown)
        4. Keep labels concise but descriptive (max 80 characters each)
        5. Create nodes depending on text complexity
        6. Focus on logical flow and hierarchical relationships
        7. Ensure all referenced indices exist in the nodes array
        8. Make the flowchart educational and easy to follow
        
        ⚠️ CRITICAL LANGUAGE REQUIREMENT: 
        - You MUST respond STRICTLY in {language} language
        - ALL node labels, title, and content must be written in {language} ONLY
        - Do NOT use Portuguese, Spanish, or any other language
        - Translate all concepts from input text to {language}
        - This is MANDATORY and NON-NEGOTIABLE
        - Ignore any language detection from input text - use {language} ONLY

        Return ONLY the JSON response, no additional text or formatting.
        """
        
        # Enhance with personalization
        return enhance_prompt_with_personalization(base_prompt, userId)
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the Gemini API response."""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove any markdown code blocks if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:-3]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:-3]
            
            # Parse JSON
            parsed_data = json.loads(cleaned_text)
            
            # Validate required structure
            if not isinstance(parsed_data, dict):
                raise ValueError("Response must be a dictionary")
            
            if "title" not in parsed_data or "flowchart" not in parsed_data:
                raise ValueError("Response must contain 'title' and 'flowchart' fields")
            
            if "nodes" not in parsed_data["flowchart"]:
                raise ValueError("Flowchart must contain 'nodes' field")
            
            if not isinstance(parsed_data["flowchart"]["nodes"], list):
                raise ValueError("Nodes must be a list")
            
            # Validate each node
            for i, node in enumerate(parsed_data["flowchart"]["nodes"]):
                if not isinstance(node, dict):
                    raise ValueError(f"Node {i} must be a dictionary")
                
                if "label" not in node:
                    raise ValueError(f"Node {i} must have a 'label' field")
                
                if "children" in node and node["children"] is not None:
                    if not isinstance(node["children"], list):
                        raise ValueError(f"Node {i} children must be a list or null")
                    
                    # Validate child indices
                    for child_idx in node["children"]:
                        if not isinstance(child_idx, int) or child_idx < 0 or child_idx >= len(parsed_data["flowchart"]["nodes"]):
                            raise ValueError(f"Node {i} has invalid child index: {child_idx}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing response: {str(e)}")
    
    def _create_fallback_flowchart(self, text: str, language: Optional[str] = "English") -> Dict[str, Any]:
        """Create a simple fallback flowchart when AI generation fails."""
        # Extract first few sentences or concepts for a basic flowchart
        sentences = text.split('.')[:3]
        
        # Language-specific titles
        title_translations = {
            "English": "Text Analysis Flowchart",
            "Spanish": "Diagrama de Flujo de Análisis de Texto",
            "French": "Organigramme d'Analyse de Texte",
            "German": "Textanalyse-Flussdiagramm",
            "Portuguese": "Fluxograma de Análise de Texto",
            "Italian": "Diagramma di Flusso per l'Analisi del Testo",
            "Chinese": "文本分析流程图",
            "Japanese": "テキスト解析フローチャート",
            "Korean": "텍스트 분석 순서도",
            "Russian": "Блок-схема анализа текста",
            "Arabic": "مخطط تدفق تحليل النص",
            "Hindi": "पाठ विश्लेषण प्रवाह चार्ट"
        }
        
        # Language-specific main topic labels
        main_topic_translations = {
            "English": "Main Topic",
            "Spanish": "Tema Principal",
            "French": "Sujet Principal",
            "German": "Hauptthema",
            "Portuguese": "Tópico Principal",
            "Italian": "Argomento Principale",
            "Chinese": "主要话题",
            "Japanese": "メイントピック",
            "Korean": "주요 주제",
            "Russian": "Основная тема",
            "Arabic": "الموضوع الرئيسي",
            "Hindi": "मुख्य विषय"
        }
        
        title = title_translations.get(language or "English", title_translations["English"])
        main_topic_label = main_topic_translations.get(language or "English", main_topic_translations["English"])
        
        nodes = [
            {
                "label": main_topic_label,
                "children": [1] if len(sentences) > 1 else None
            }
        ]
        
        for i, sentence in enumerate(sentences[1:], 1):
            clean_sentence = sentence.strip()[:80]  # Limit length
            if clean_sentence:
                nodes.append({
                    "label": clean_sentence,
                    "children": [i + 1] if i < len(sentences) - 1 else None
                })
        
        return {
            "title": title,
            "flowchart": {
                "nodes": nodes
            }
        }

    async def generate_flowchart(self, text: str, instruction: Optional[str] = None, userId: Optional[str] = None, language: Optional[str] = "English") -> flowchart_response:
        """
        Generate a flowchart based on the provided text using Gemini AI.
        
        Args:
            text (str): The input text to create a flowchart from
            instruction (Optional[str]): Optional instruction for flowchart generation
            userId (Optional[str]): Optional user ID for personalization
            
        Returns:
            flowchart_response: The generated flowchart with title and nodes
        """
        try:
            # Create the personalized prompt
            prompt = self._create_flowchart_prompt(text, instruction, userId, language)

            # Add additional system instruction to the prompt for language enforcement
            enhanced_prompt = f"""SYSTEM INSTRUCTION: You are a multilingual educational assistant. You MUST respond strictly in {language} language only, regardless of the input text language. Always translate concepts to {language} if needed.

{prompt}"""

            # Debug: Print language being used
            print(f"DEBUG: Flowchart generation requested in language: {language}")
            print(f"DEBUG: Enhanced prompt includes language enforcement for: {language}")

            # Generate content using Gemini
            response = client.models.generate_content(model="gemini-2.0-flash", contents=enhanced_prompt, config={"response_mime_type": "application/json"})
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Debug: Check response language
            print(f"DEBUG: Raw response preview: {response.text[:200]}...")

            # Parse the response
            parsed_data = self._parse_gemini_response(response.text)
            
            # Additional language validation
            title = parsed_data.get("title", "")
            # Check for Portuguese words in title
            portuguese_indicators = ["inteligência", "máquinas", "aprendizado", "tecnologia", "processamento", "linguagem"]
            if language == "English" and any(word in title.lower() for word in portuguese_indicators):
                print(f"WARNING: Generated title '{title}' appears to contain Portuguese words despite English request")
                # Force English title
                parsed_data["title"] = "Artificial Intelligence Concepts"
                
            # Check for Portuguese words in node labels
            for node in parsed_data.get("flowchart", {}).get("nodes", []):
                node_label = node.get("label", "")
                if language == "English" and any(word in node_label.lower() for word in portuguese_indicators):
                    print(f"WARNING: Node label '{node_label}' appears to contain Portuguese words")
                    # You could implement translation here if needed            # Convert to Pydantic models
            nodes = []
            for node_data in parsed_data["flowchart"]["nodes"]:
                nodes.append(Node(
                    label=node_data["label"],
                    children=node_data.get("children")
                ))
            
            flowchart_nodes = Nodes(nodes=nodes)
            
            return flowchart_response(
                title=parsed_data["title"],
                flowchart=flowchart_nodes
            )
            
        except Exception as e:
            print(f"Error generating flowchart: {str(e)}")
            # Use fallback flowchart
            fallback_data = self._create_fallback_flowchart(text, language)
            
            # Convert fallback to Pydantic models
            nodes = []
            for node_data in fallback_data["flowchart"]["nodes"]:
                nodes.append(Node(
                    label=node_data["label"],
                    children=node_data.get("children")
                ))
            
            flowchart_nodes = Nodes(nodes=nodes)
            
            return flowchart_response(
                title=fallback_data["title"],
                flowchart=flowchart_nodes
            )

# Global instance
flowchart_generator = FlowchartGenerator()

async def create_flowchart_logic(text: str, instruction: Optional[str] = None, userId: Optional[str] = None, language: Optional[str] = "English") -> flowchart_response:
    """
    Main function to create flowchart logic based on input text.
    
    Args:
        text (str): The input text to analyze and create flowchart from
        instruction (Optional[str]): Optional instruction for flowchart generation
        userId (Optional[str]): Optional user ID for personalization
        
    Returns:
        flowchart_response: Generated flowchart with title and hierarchical nodes
    """
    return await flowchart_generator.generate_flowchart(text, instruction, userId, language)