#screenshot_analysis.py
import os
import base64
import json
import time
from datetime import datetime
from PIL import ImageGrab, Image
import win32clipboard
import threading
from io import BytesIO
from openai import OpenAI
from pystray import Icon, Menu, MenuItem
import sys
import easyocr
import numpy as np

class ScreenshotAnalyzer:
    def __init__(self, api_key):
        """Initialize the ScreenshotAnalyzer with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.screenshots_dir = "screenshots"
        self.analysis_file = os.path.join(self.screenshots_dir, "screenshot_analysis.json")
        self._ensure_screenshots_directory()
        self._ensure_analysis_file()
        self.is_running = True
        self.last_clipboard_content = None
        self.clipboard_lock = threading.Lock()
        print("Initializing OCR reader (this may take a moment on first run)...")
        self.reader = easyocr.Reader(['en'])

    def engineer_prompt(self, text_analysis, vision_analysis):
        """Generate an engineered prompt based on the analysis results."""
        try:
            print("Engineering prompt...")
            prompt_engineering_messages = [
                {
                    "role": "system",
                    "content": """You are an AI prompt engineer for a screenshot analysis tool. Your task is to create a targeted prompt based on the following rules:

                    1. For error messages or coding issues:
                       - Create a debugging-focused prompt that asks for specific solutions
                       - Include error context and potential impact

                    2. For document/presentation content:
                       - Create a summarization prompt
                       - Ask for key points and main ideas
                       - Request actionable insights

                    3. For code compilation errors:
                       - Create a prompt focused on identifying the root cause
                       - Ask for step-by-step solutions
                       - Request best practices to avoid similar issues

                    4. For coding tasks/requirements:
                       - Create a prompt for generating appropriate code
                       - Include performance and scalability considerations
                       - Ask for explanations of the approach

                    5. For terminal outputs:
                       - Create a prompt focusing on command interpretation
                       - Ask for error resolution if applicable
                       - Request command alternatives if relevant

                    Analyze the provided text and vision analysis to determine the type of content and create the most appropriate prompt."""
                },
                {
                    "role": "user",
                    "content": f"""Create a targeted prompt based on these analyses:

                    TEXT ANALYSIS:
                    {text_analysis}

                    VISION ANALYSIS:
                    {vision_analysis}

                    Generate a prompt that will get the most relevant and useful response for this type of content."""
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=prompt_engineering_messages,
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error engineering prompt: {e}")
            return "Error generating prompt"

    def get_ai_result(self, engineered_prompt, text_analysis, vision_analysis):
        """Get AI result based on the engineered prompt."""
        try:
            print("Generating AI result...")
            result_messages = [
                {
                    "role": "system",
                    "content": """You are an AI assistant specialized in analyzing screenshots and providing detailed solutions. 
                    Your responses should be clear, actionable, and directly address the user's needs."""
                },
                {
                    "role": "user",
                    "content": f"""Based on the following information:

                    Text Analysis: {text_analysis}
                    Vision Analysis: {vision_analysis}
                    
                    Please respond to this prompt:
                    {engineered_prompt}"""
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=result_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting AI result: {e}")
            return "Error generating result"

    def _ensure_screenshots_directory(self):
        """Create screenshots directory if it doesn't exist."""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)

    def _ensure_analysis_file(self):
        """Create or load the analysis JSON file."""
        if not os.path.exists(self.analysis_file):
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)

    def _load_analyses(self):
        """Load existing analyses from the JSON file."""
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        except FileNotFoundError:
            return {}

    def _save_analyses(self, analyses):
        """Save analyses to the JSON file."""
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, indent=4, ensure_ascii=False)

    def _get_clipboard_image(self):
        """Get image from clipboard with proper resource management."""
        if not self.clipboard_lock.acquire(timeout=1):
            return None

        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                try:
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                    if data:
                        image_stream = BytesIO(data)
                        try:
                            image = Image.open(image_stream)
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            return image.copy()
                        finally:
                            image_stream.close()
                except Exception as e:
                    print(f"Error processing clipboard data: {e}")
                    return None
        except Exception as e:
            print(f"Error accessing clipboard: {e}")
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            self.clipboard_lock.release()

        return None

    def _encode_image(self, image_path):
        """Encode the image to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    def save_screenshot(self, image):
        """Save the screenshot and return the filepath."""
        if image is None:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)

        try:
            image.save(filepath, 'PNG')
            return filepath
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None

    def extract_text_from_image(self, image_path):
        """Extract text from the image using EasyOCR."""
        try:
            results = self.reader.readtext(image_path)
            extracted_text = []
            for detection in results:
                text = detection[1]
                extracted_text.append(text)
            return '\n'.join(extracted_text)
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def get_final_solution(self, text_analysis, vision_analysis, engineered_prompt, ai_result):
        """Generate a final, refined solution based on all previous analyses."""
        try:
            print("Generating final solution...")
            solution_messages = [
                {
                    "role": "system",
                    "content": """You are an AI solution generator that provides clear, concise, and actionable outputs based on screenshot analysis. Your task is to provide solutions in these categories:

    1. For Error Screenshots:
    - Direct solution steps
    - Code fixes if applicable
    - Prevention tips

    2. For Documents/Text:
    - Concise summary
    - Key action items
    - Main takeaways

    3. For Visual Identification:
    - Detailed identification (person, object, scene)
    - Key characteristics
    - Relevant context

    4. For Code/Technical Screenshots:
    - Code solutions
    - Implementation steps
    - Best practices

    5. For Task Requirements:
    - Clear deliverables
    - Implementation approach
    - Resource needs

    Your response should be direct, practical, and immediately useful."""
                },
                {
                    "role": "user",
                    "content": f"""Based on all previous analyses:

    Text Analysis: {text_analysis}
    Vision Analysis: {vision_analysis}
    Engineered Prompt: {engineered_prompt}
    AI Result: {ai_result}

    Provide a refined, final solution that directly addresses what's shown in the screenshot. 
    If it's an error, provide the solution. 
    If it's an image of something/someone, provide identification and details. 
    If it's code, provide the solution/implementation. 
    If it's a document, provide the key insights.
    Make the response direct, practical, and immediately useful."""
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=solution_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating final solution: {e}")
            return "Error generating final solution"
    def analyze_screenshot(self, image_path):
        """Analyze the screenshot using OCR, Vision capabilities, and generate results."""
        if not image_path:
            return ("Error: No image path provided", 
                    "Error: No image path provided", 
                    "Error: No image path provided",
                    "Error: No image path provided")

        try:
            # 1. Text Analysis using OCR
            print("Extracting text from image...")
            extracted_text = self.extract_text_from_image(image_path)
            
            text_analysis = "No text could be extracted from the image."
            if extracted_text.strip():
                print("Analyzing extracted text...")
                text_messages = [
                    {
                        "role": "system",
                        "content": """You are an advanced text analyzer specialized in identifying different types of content from screenshots. Your task is to analyze the text and categorize it into one of these types:

    1. Error Messages: Identify any error messages, stack traces, or warning messages
    2. Documentation/Presentation: Detect if the content is from documents, slides, or educational material
    3. Code/Terminal Output: Recognize code snippets, compilation errors, or terminal outputs
    4. Task Requirements: Identify if the text contains coding tasks or requirements
    5. General Content: Any other type of content

    For each type, extract specific information that will be useful for generating solutions or summaries."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this extracted text and provide a structured analysis with the following:

    1. Content Type Classification:
    - Primary category (Error/Documentation/Code/Task/General)
    - Confidence level in classification
    - Subcategory if applicable

    2. Key Elements:
    - For Errors: Error type, error message, context, affected components
    - For Documentation: Main topics, key points, important concepts
    - For Code: Language, framework, specific issues or requirements
    - For Tasks: Requirements, constraints, expected outcomes
    - For General: Main subject, important details, context

    3. Technical Details:
    - Any technical terms, version numbers, or specific identifiers
    - Related technologies or frameworks mentioned
    - Dependencies or environmental factors

    4. Action Items:
    - What needs to be solved/summarized/generated
    - Critical information for generating a solution
    - Potential approach suggestions

    Extracted text:
    {extracted_text}"""
                    }
                ]

                text_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=text_messages,
                    max_tokens=500,
                    temperature=0.7
                )
                text_analysis = text_response.choices[0].message.content

            # 2. Vision Analysis
            print("Performing vision analysis...")
            base64_image = self._encode_image(image_path)
            
            vision_messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this screenshot with focus on these aspects:

    1. Interface Context:
    - Is this an IDE, terminal, document viewer, or other application?
    - What specific application or environment is shown?
    - Are there any error indicators, warning symbols, or status indicators?

    2. Visual Structure:
    - Layout of error messages or code blocks
    - Presence of line numbers, file paths, or navigation elements
    - Color coding or syntax highlighting that indicates errors or specific content types

    3. Supporting Elements:
    - Are there related UI elements like buttons, menus, or tooltips?
    - Are there any visual cues about the type of content (error icons, info badges)?
    - Are there any highlighted or emphasized sections?

    4. Technical Context:
    - Any visible file names, paths, or URLs
    - Version numbers or environment information
    - Timestamps or sequence indicators

    Provide a detailed analysis that will help in determining the appropriate response to this screenshot's content."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "auto"
                            }
                        }
                    ]
                }
            ]

            vision_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=vision_messages,
                max_tokens=300
            )
            vision_analysis = vision_response.choices[0].message.content

            # 3. Generate engineered prompt
            print("Engineering prompt based on analysis...")
            engineered_prompt = self.engineer_prompt(text_analysis, vision_analysis)

            # 4. Get AI result
            print("Generating final result...")
            ai_result = self.get_ai_result(engineered_prompt, text_analysis, vision_analysis)

            print("Generating final solution...")
            final_solution = self.get_final_solution(
                text_analysis, 
                vision_analysis, 
                engineered_prompt, 
                ai_result
            )    

            return text_analysis, vision_analysis, engineered_prompt, ai_result, final_solution
            

        except Exception as e:
            print(f"Error in complete analysis: {e}")
            return (f"Error analyzing screenshot: {str(e)}", 
                    f"Error analyzing screenshot: {str(e)}", 
                    "Error generating prompt",
                    "Error generating result",
                    "Error generating final solution")

    def save_analysis(self, image_path, analysis_results):
        """Save complete analysis to the consolidated JSON file."""
        try:
            # Unpack the analysis results
            text_analysis, vision_analysis, engineered_prompt, ai_result, final_solution = analysis_results
            
            # Load existing analyses
            analyses = self._load_analyses()
            
            # Create new analysis entry
            filename = os.path.basename(image_path)
            analyses[filename] = {
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "text_analysis": text_analysis,
                "vision_analysis": vision_analysis,
                "engineered_prompt": engineered_prompt,
                "ai_result": ai_result,
                "final_solution": final_solution
            }
            
            # Save updated analyses
            self._save_analyses(analyses)
            
            return self.analysis_file
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return None


    def monitor_clipboard(self):
        """Monitor clipboard for new screenshots."""
        print("Monitoring for screenshots... Press Win+Shift+S to capture.")
        print("The program is running in the background. Check the system tray icon.")

        while self.is_running:
            try:
                if not self.is_running:
                    break

                image = self._get_clipboard_image()
                if image:
                    current_content = hash(image.tobytes())

                    if current_content != self.last_clipboard_content:
                        self.last_clipboard_content = current_content

                        image_path = self.save_screenshot(image)
                        if image_path:
                            print(f"\nScreenshot saved: {image_path}")

                            print("Analyzing screenshot...")
                            analysis_results = self.analyze_screenshot(image_path)

                            if analysis_results:
                                analysis_path = self.save_analysis(image_path, analysis_results)
                                if analysis_path:
                                    print(f"Analysis saved to: {analysis_path}")
                                    print("Analysis includes both text and vision analysis")
                                else:
                                    print("Error: Could not save analysis")
                                print("\nReady for next screenshot...")

                    image.close()

                time.sleep(0.5)

            except Exception as e:
                print(f"Error in clipboard monitoring: {e}")
                time.sleep(1)

    def stop(self):
        """Stop the monitoring."""
        self.is_running = False


def create_system_tray(analyzer):
    """Create system tray icon and menu."""
    def on_exit(icon, item):
        print("Shutting down...")
        analyzer.stop()
        icon.stop()

    icon_image = Image.new('RGB', (64, 64), color='blue')

    menu = Menu(
        MenuItem("Screenshot Analyzer Running", lambda: None, enabled=False),
        MenuItem("Exit", on_exit)
    )

    icon = Icon("ScreenshotAnalyzer", icon_image, "Screenshot Analyzer", menu)
    return icon


def main():
    # Replace with your actual OpenAI API key
    api_key = OPENAI_API_KEY_HERE

    try:
        analyzer = ScreenshotAnalyzer(api_key)

        monitor_thread = threading.Thread(target=analyzer.monitor_clipboard, daemon=True)
        monitor_thread.start()

        icon = create_system_tray(analyzer)
        icon.run()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Program terminated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
