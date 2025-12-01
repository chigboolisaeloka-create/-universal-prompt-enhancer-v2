import streamlit as st
import os
import time
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION (Must be first Streamlit command)
# ============================================================================

st.set_page_config(
    page_title="Universal Prompt Enhancer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS
# ============================================================================

class TechniqueKeys:
    """Constants for technique dictionary keys."""
    ROLE = 'role'
    COT = 'cot'
    FORMAT = 'format'
    FORMAT_DETAILS = 'format_details'
    CONTEXT = 'context'
    ITERATE = 'iterate'
    ITERATE_INSTRUCTIONS = 'iterate_instructions'
    NEGATIVE = 'negative'
    NEGATIVE_DETAILS = 'negative_details'

# Available models
MODELS = {
    "Gemini 2.5 Flash (Fast)": "gemini-2.5-flash",
    "Gemini 1.5 Flash (Fastest)": "gemini-1.5-flash",
    "Gemini 1.5 Pro (Most Capable)": "gemini-1.5-pro"
}

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PresetConfig:
    """Configuration for a prompting technique preset."""
    role: bool = True
    cot: bool = False
    format: bool = False
    context: bool = True
    iterate: bool = False
    negative: bool = False

# Preset configurations for beginners
PRESETS: Dict[str, Optional[PresetConfig]] = {
    "Custom (Manual)": None,
    "📝 Content Writer": PresetConfig(role=True, cot=False, format=True, context=True, iterate=False, negative=True),
    "💻 Code Generator": PresetConfig(role=True, cot=True, format=True, context=True, iterate=False, negative=True),
    "🎓 Learning Assistant": PresetConfig(role=True, cot=True, format=False, context=True, iterate=False, negative=False),
    "✨ All Techniques": PresetConfig(role=True, cot=True, format=True, context=True, iterate=True, negative=True)
}

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

# Load environment variables
load_dotenv()

def get_api_key() -> Optional[str]:
    """Get API key from Streamlit secrets (cloud) or environment (local)."""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        if 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except (FileNotFoundError, KeyError):
        pass
    # Fall back to environment variable (for local development)
    return os.getenv('GEMINI_API_KEY')

@st.cache_resource
def initialize_gemini_client(api_key: str) -> genai.Client:
    """Initialize and cache the Gemini client to avoid recreation on every rerun."""
    logger.info("Initializing Gemini client")
    return genai.Client(api_key=api_key)

# Get and validate API key
api_key = get_api_key()

if not api_key or api_key == "YOUR_API_KEY_HERE" or api_key == "your_actual_api_key_here":
    st.error("⚠️ **API Key Missing or Invalid**")
    st.warning("""
    **For local development:** Add your API key to the `.env` file  
    **For deployment:** Configure it in your platform's secrets management
    
    Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
    """)
    st.stop()

# Initialize Gemini client (cached)
client = initialize_gemini_client(api_key)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_custom_css() -> None:
    """Load custom CSS styling."""
    css = """
    <style>
        /* Main Header - Responsive Font Size */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #FF4B4B 0%, #FF8E53 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        @media (max-width: 768px) {
            .main-header {
                font-size: 1.8rem;
            }
        }

        /* Subtitle - Responsive Font Size */
        .subtitle {
            font-size: 1.1rem;
            color: var(--text-color);
            opacity: 0.8;
            margin-bottom: 2rem;
        }
        @media (max-width: 768px) {
            .subtitle {
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
            }
        }

        /* Text Area Font */
        .stTextArea textarea {
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        }

        /* Example Box - Theming Support */
        .example-box {
            background-color: var(--secondary-background-color);
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 3px solid #FF4B4B;
            margin: 0.5rem 0;
        }

        /* Stat Box - Theming Support */
        .stat-box {
            background-color: var(--secondary-background-color);
            padding: 0.75rem;
            border-radius: 0.5rem;
            text-align: center;
            border: 1px solid rgba(128, 128, 128, 0.2);
        }

        /* Technique Box - Theming Support */
        .technique-box {
            background-color: var(--secondary-background-color);
            padding: 0.5rem;
            border-radius: 0.3rem;
            margin: 0.3rem 0;
            border-left: 2px solid #4CAF50;
            border: 1px solid rgba(128, 128, 128, 0.2);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def validate_techniques(techniques: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure technique dictionary has all required keys with defaults."""
    defaults = {
        TechniqueKeys.ROLE: False,
        TechniqueKeys.COT: False,
        TechniqueKeys.FORMAT: False,
        TechniqueKeys.FORMAT_DETAILS: '',
        TechniqueKeys.CONTEXT: False,
        TechniqueKeys.ITERATE: False,
        TechniqueKeys.ITERATE_INSTRUCTIONS: '',
        TechniqueKeys.NEGATIVE: False,
        TechniqueKeys.NEGATIVE_DETAILS: ''
    }
    return {**defaults, **techniques}

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input to prevent issues."""
    # Remove null bytes
    text = text.replace('\x00', '')
    # Limit length
    if len(text) > max_length:
        st.warning(f"⚠️ Input truncated to {max_length} characters")
        text = text[:max_length]
    return text.strip()

def build_enhanced_prompt(
    raw_input: str, 
    techniques: Dict[str, Any], 
    role_persona: str, 
    tone_style: str, 
    context_file_content: str
) -> str:
    """Build the enhanced prompt based on selected techniques."""
    
    # Validate techniques dictionary
    techniques = validate_techniques(techniques)
    
    prompt_parts: List[str] = []
    
    # Base instruction
    prompt_parts.append("Create an enhanced, professional prompt based on the following specifications:")
    prompt_parts.append("")
    
    # 1. Role Assignment
    if techniques.get(TechniqueKeys.ROLE):
        prompt_parts.append(f"**ROLE/EXPERTISE:** {role_persona}")
        prompt_parts.append("")
    
    # 2. Context Setting
    if techniques.get(TechniqueKeys.CONTEXT) and context_file_content and context_file_content != "No external context file was provided.":
        prompt_parts.append("**CONTEXT:**")
        prompt_parts.append(context_file_content)
        prompt_parts.append("")
    
    # 3. Constraint & Format
    if techniques.get(TechniqueKeys.FORMAT) and techniques.get(TechniqueKeys.FORMAT_DETAILS):
        prompt_parts.append(f"**OUTPUT FORMAT:** {techniques[TechniqueKeys.FORMAT_DETAILS]}")
        prompt_parts.append("")
    
    # 4. Tone/Style
    prompt_parts.append(f"**TONE/STYLE:** {tone_style}")
    prompt_parts.append("")
    
    # 5. Chain of Thought
    if techniques.get(TechniqueKeys.COT):
        prompt_parts.append("**REASONING:** Show your step-by-step thought process and reasoning before providing the final answer.")
        prompt_parts.append("")
    
    # 6. Iteration & Critique (for refinement)
    if techniques.get(TechniqueKeys.ITERATE) and techniques.get(TechniqueKeys.ITERATE_INSTRUCTIONS):
        prompt_parts.append(f"**REFINEMENT INSTRUCTIONS:** {techniques[TechniqueKeys.ITERATE_INSTRUCTIONS]}")
        prompt_parts.append("")
    
    # 7. Negative Constraints
    if techniques.get(TechniqueKeys.NEGATIVE) and techniques.get(TechniqueKeys.NEGATIVE_DETAILS):
        prompt_parts.append(f"**EXCLUDE:** {techniques[TechniqueKeys.NEGATIVE_DETAILS]}")
        prompt_parts.append("")
    
    # Raw input/task
    prompt_parts.append("**TASK:**")
    prompt_parts.append(raw_input)
    prompt_parts.append("")
    
    # Final instruction
    prompt_parts.append("---")
    prompt_parts.append("Based on the above specifications, create a clear, structured, and professional prompt.")
    
    return "\n".join(prompt_parts)

def check_rate_limit() -> None:
    """Ensure minimum time between API calls to prevent rate limiting."""
    if 'last_api_call' not in st.session_state:
        st.session_state.last_api_call = 0
    
    time_since_last = time.time() - st.session_state.last_api_call
    if time_since_last < 1:  # Minimum 1 second between calls
        time.sleep(1 - time_since_last)

def update_api_call_time() -> None:
    """Update the timestamp of the last API call."""
    st.session_state.last_api_call = time.time()

def export_history_as_json() -> str:
    """Export prompt history as JSON string."""
    if st.session_state.prompt_history:
        return json.dumps(st.session_state.prompt_history, indent=2)
    return json.dumps([])

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'prompt_history' not in st.session_state:
    st.session_state.prompt_history = []

if 'current_output' not in st.session_state:
    st.session_state.current_output = None

if 'selected_preset' not in st.session_state:
    st.session_state.selected_preset = "Custom (Manual)"

if 'custom_presets' not in st.session_state:
    st.session_state.custom_presets = {}

if 'last_api_call' not in st.session_state:
    st.session_state.last_api_call = 0

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================



# Load custom CSS
load_custom_css()

# ============================================================================
# SIDEBAR - CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Model selection
    selected_model_name = st.selectbox(
        "Select Model",
        options=list(MODELS.keys()),
        index=0,
        help="Choose the Gemini model for generation"
    )
    model_id = MODELS[selected_model_name]
    
    # Temperature/Creativity slider
    temperature = st.slider(
        "Creativity Level",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Higher values make output more creative but less focused"
    )
    
    st.markdown("---")
    
    st.markdown("### 🎭 Persona & Tone")
    
    role_persona = st.text_area(
        "AI's Role",
        value="A Senior AI Prompt Engineering Expert specialized in business-to-business (B2B) content marketing.",
        height=100,
        help="Define the role/expertise of the AI"
    )
    
    tone_style = st.text_input(
        "Desired Tone/Style",
        value="Formal, Actionable, and structured using markdown headings.",
        help="Specify the writing style"
    )
    
    st.markdown("---")
    
    st.markdown("### 🧠 Prompting Techniques")
    
    # Combine default and custom presets
    all_presets = {**PRESETS}
    if st.session_state.custom_presets:
        all_presets.update({f"⭐ {name}": PresetConfig(**config) for name, config in st.session_state.custom_presets.items()})
    
    # Preset selector
    selected_preset = st.selectbox(
        "Quick Presets",
        options=list(all_presets.keys()),
        help="Choose a preset or customize manually"
    )
    
    # Update session state if preset changes
    if selected_preset != st.session_state.selected_preset:
        st.session_state.selected_preset = selected_preset
    
    # Get preset values or use custom
    preset_values = all_presets.get(selected_preset)
    
    # Show individual technique toggles
    with st.expander("🔧 Advanced Techniques", expanded=(selected_preset == "Custom (Manual)")):
        st.caption("Enable specific prompting techniques")
        
        use_role = st.checkbox(
            "1️⃣ Role Assignment",
            value=preset_values.role if preset_values else True,
            help="Establishes the LLM's expertise and authority",
            disabled=preset_values is not None
        )
        
        use_cot = st.checkbox(
            "2️⃣ Chain-of-Thought",
            value=preset_values.cot if preset_values else False,
            help="Forces step-by-step logical reasoning",
            disabled=preset_values is not None
        )
        
        use_format = st.checkbox(
            "3️⃣ Constraint & Format",
            value=preset_values.format if preset_values else False,
            help="Defines exact structure and style of output",
            disabled=preset_values is not None
        )
        
        if use_format or (preset_values and preset_values.format):
            format_details = st.text_input(
                "Format instructions",
                value="Respond in clear markdown with headings",
                placeholder="e.g., 'Use bullet points' or 'Maximum 200 words'"
            )
        else:
            format_details = ""
        
        use_context = st.checkbox(
            "4️⃣ Context Setting",
            value=preset_values.context if preset_values else True,
            help="Uses uploaded context file if available",
            disabled=preset_values is not None
        )
        
        use_iterate = st.checkbox(
            "5️⃣ Iteration & Critique",
            value=preset_values.iterate if preset_values else False,
            help="Refines previous answers",
            disabled=preset_values is not None
        )
        
        if use_iterate or (preset_values and preset_values.iterate):
            iterate_instructions = st.text_area(
                "Refinement instructions",
                value="Review and improve clarity and structure",
                placeholder="e.g., 'Make code PEP8 compliant' or 'Add more examples'",
                height=70
            )
        else:
            iterate_instructions = ""
        
        use_negative = st.checkbox(
            "6️⃣ Negative Constraints",
            value=preset_values.negative if preset_values else False,
            help="Excludes specific content from response",
            disabled=preset_values is not None
        )
        
        if use_negative or (preset_values and preset_values.negative):
            negative_details = st.text_input(
                "Exclude from response",
                value="",
                placeholder="e.g., 'Do not include pricing information'"
            )
        else:
            negative_details = ""
    
    # Save custom preset
    if selected_preset == "Custom (Manual)":
        with st.expander("💾 Save Current Configuration"):
            preset_name = st.text_input("Preset name:", key="save_preset_name")
            if st.button("Save as Preset", use_container_width=True):
                if preset_name:
                    custom_config = {
                        TechniqueKeys.ROLE: use_role,
                        TechniqueKeys.COT: use_cot,
                        TechniqueKeys.FORMAT: use_format,
                        TechniqueKeys.CONTEXT: use_context,
                        TechniqueKeys.ITERATE: use_iterate,
                        TechniqueKeys.NEGATIVE: use_negative
                    }
                    st.session_state.custom_presets[preset_name] = custom_config
                    st.success(f"✅ Saved preset: {preset_name}")
                    st.rerun()
                else:
                    st.error("Please enter a preset name")
    
    # Compile technique dictionary
    if preset_values:
        techniques = {
            TechniqueKeys.ROLE: preset_values.role,
            TechniqueKeys.COT: preset_values.cot,
            TechniqueKeys.FORMAT: preset_values.format,
            TechniqueKeys.FORMAT_DETAILS: format_details if preset_values.format else "",
            TechniqueKeys.CONTEXT: preset_values.context,
            TechniqueKeys.ITERATE: preset_values.iterate,
            TechniqueKeys.ITERATE_INSTRUCTIONS: iterate_instructions if preset_values.iterate else "",
            TechniqueKeys.NEGATIVE: preset_values.negative,
            TechniqueKeys.NEGATIVE_DETAILS: negative_details if preset_values.negative else ""
        }
    else:
        techniques = {
            TechniqueKeys.ROLE: use_role,
            TechniqueKeys.COT: use_cot,
            TechniqueKeys.FORMAT: use_format,
            TechniqueKeys.FORMAT_DETAILS: format_details,
            TechniqueKeys.CONTEXT: use_context,
            TechniqueKeys.ITERATE: use_iterate,
            TechniqueKeys.ITERATE_INSTRUCTIONS: iterate_instructions,
            TechniqueKeys.NEGATIVE: use_negative,
            TechniqueKeys.NEGATIVE_DETAILS: negative_details
        }
    
    st.markdown("---")
    
    st.markdown("### 📄 Context File")
    context_file = st.file_uploader(
        "Upload Context (Optional)",
        type=['txt', 'md'],
        help="Upload a file with additional context for the AI"
    )
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.prompt_history = []
            st.session_state.current_output = None
            st.rerun()
    
    with col2:
        if st.session_state.prompt_history:
            history_json = export_history_as_json()
            st.download_button(
                label="📊 Export JSON",
                data=history_json,
                file_name="prompt_history.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit & Gemini AI")

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<h1 class="main-header">✨ Universal Prompt Enhancer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform raw ideas into structured, professional prompts using AI + Advanced Techniques</p>', unsafe_allow_html=True)

# Show active techniques
active_techniques = [k for k, v in techniques.items() if v and k not in [TechniqueKeys.FORMAT_DETAILS, TechniqueKeys.ITERATE_INSTRUCTIONS, TechniqueKeys.NEGATIVE_DETAILS]]
if active_techniques:
    st.markdown("**🔥 Active Techniques:**")
    cols = st.columns(min(len(active_techniques), 3))
    technique_names = {
        TechniqueKeys.ROLE: '1️⃣ Role',
        TechniqueKeys.COT: '2️⃣ Chain-of-Thought',
        TechniqueKeys.FORMAT: '3️⃣ Format',
        TechniqueKeys.CONTEXT: '4️⃣ Context',
        TechniqueKeys.ITERATE: '5️⃣ Iteration',
        TechniqueKeys.NEGATIVE: '6️⃣ Negative'
    }
    for idx, tech in enumerate(active_techniques):
        with cols[idx % 3]:
            st.markdown(f'<div class="technique-box">{technique_names.get(tech, tech)}</div>', unsafe_allow_html=True)
    st.markdown("")

# Example prompts
with st.expander("💡 See Example Prompts"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="example-box">', unsafe_allow_html=True)
        st.markdown("**Marketing Email**")
        st.code("Write an email about our new product launch targeting enterprise customers", language="text")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="example-box">', unsafe_allow_html=True)
        st.markdown("**Technical Doc**")
        st.code("Create API documentation for our authentication endpoints", language="text")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="example-box">', unsafe_allow_html=True)
        st.markdown("**Social Media**")
        st.code("Draft LinkedIn post about AI trends for technology leaders", language="text")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="example-box">', unsafe_allow_html=True)
        st.markdown("**Content Brief**")
        st.code("Outline a blog post about sustainable business practices", language="text")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### 📝 Enter Your Raw Prompt")

# Input area with character counter
raw_input = st.text_area(
    "Your raw, unstructured prompt",
    height=150,
    placeholder="Example: Write an email about the new feature...",
    label_visibility="collapsed"
)

# Character count
if raw_input:
    char_count = len(raw_input)
    word_count = len(raw_input.split())
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        st.markdown(f'<div class="stat-box">📊 {char_count} characters</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box">📝 {word_count} words</div>', unsafe_allow_html=True)

st.markdown("")

# Generate buttons
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    generate_btn = st.button("🚀 Generate Enhanced Prompt", type="primary", use_container_width=True)
with col2:
    generate_variations_btn = st.button("🔄 Generate 3 Variations", use_container_width=True)

# ============================================================================
# GENERATION LOGIC
# ============================================================================

def generate_prompt(temp_override: Optional[float] = None) -> None:
    """Generate a single enhanced prompt."""
    if not raw_input:
        st.error("⚠️ Please enter some raw input to enhance.")
        return
    
    # Sanitize input
    sanitized_input = sanitize_input(raw_input)
    
    # Load context file content
    context_file_content = "No external context file was provided."
    if context_file is not None:
        try:
            context_file_content = context_file.read().decode("utf-8")
        except Exception as e:
            logger.error(f"Error reading context file: {e}")
            st.warning(f"Could not read context file: {e}")
            context_file_content = "Error reading context file."
    
    # Build the enhanced prompt using selected techniques
    full_prompt = build_enhanced_prompt(
        sanitized_input, 
        techniques, 
        role_persona, 
        tone_style, 
        context_file_content
    )
    
    # Check rate limiting
    check_rate_limit()
    
    # Show loading spinner
    with st.spinner("🤖 Enhancing your prompt with Gemini AI..."):
        try:
            # Call Gemini API
            actual_temp = temp_override if temp_override is not None else temperature
            logger.info(f"API call - Model: {model_id}, Temperature: {actual_temp}")
            
            response = client.models.generate_content(
                model=model_id,
                contents=full_prompt,
                config={'temperature': actual_temp}
            )
            
            # Update rate limit tracker
            update_api_call_time()
            
            # Store in session state
            st.session_state.current_output = response.text
            st.session_state.prompt_history.insert(0, {
                'input': sanitized_input,
                'output': response.text,
                'model': selected_model_name,
                'techniques': [t for t in active_techniques],
                'temperature': actual_temp
            })
            
            # Keep only last 5 prompts
            if len(st.session_state.prompt_history) > 5:
                st.session_state.prompt_history = st.session_state.prompt_history[:5]
            
            logger.info("Successfully generated prompt")
            
        except ClientError as e:
            logger.error(f"API Error: {str(e)}")
            st.error("❌ **API Error: Invalid API Key or Request**")
            st.error(f"**Details:** {str(e)}")
            st.info("💡 Please verify your API key configuration.")
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            st.error("❌ **An error occurred while calling the Gemini API**")
            st.exception(e)

if generate_btn:
    generate_prompt()

if generate_variations_btn:
    if not raw_input:
        st.error("⚠️ Please enter some raw input to enhance.")
    else:
        st.markdown("### 🔄 Generated Variations")
        st.caption("Three variations with different creativity levels")
        
        variations_container = st.container()
        
        with variations_container:
            for i, temp_value in enumerate([0.7, 1.0, 1.5]):
                with st.expander(f"Variation {i+1} (Temperature: {temp_value})", expanded=False):
                    generate_prompt(temp_override=temp_value)
                    if st.session_state.current_output:
                        st.code(st.session_state.current_output, language='markdown')

# ============================================================================
# OUTPUT DISPLAY
# ============================================================================

if st.session_state.current_output:
    st.markdown("---")
    st.markdown("### ✅ Enhanced Prompt")
    
    # Display the output
    st.code(st.session_state.current_output, language='markdown')
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        st.download_button(
            label="📥 Download",
            data=st.session_state.current_output,
            file_name="enhanced_prompt.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            try:
                import pyperclip
                pyperclip.copy(st.session_state.current_output)
                st.toast("Copied to clipboard! 📋", icon="✅")
            except ImportError:
                st.info("💡 Install pyperclip for clipboard support: pip install pyperclip")
            except Exception:
                st.info("💡 Please manually select and copy the text above")

# ============================================================================
# PROMPT HISTORY
# ============================================================================

if st.session_state.prompt_history:
    st.markdown("---")
    with st.expander(f"📚 Prompt History ({len(st.session_state.prompt_history)} saved)"):
        for idx, item in enumerate(st.session_state.prompt_history):
            tech_badges = " ".join([f"`{t}`" for t in item.get('techniques', [])])
            temp_info = f"Temp: {item.get('temperature', 'N/A')}"
            st.markdown(f"**#{idx + 1}** - *{item['model']}* - {temp_info} - {tech_badges}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Input:**")
                st.text(item['input'][:100] + "..." if len(item['input']) > 100 else item['input'])
            with col2:
                st.markdown("**Output:**")
                with st.expander("View enhanced prompt"):
                    st.code(item['output'], language='markdown')
            st.markdown("---")
