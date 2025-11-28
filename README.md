# ✨ Universal Prompt Enhancer

Transform raw, unstructured prompts into professional, well-crafted prompts using Google's Gemini AI. Built with Streamlit for a beautiful, intuitive interface.

## 🌟 Features

- **🤖 Multiple AI Models** - Choose from Gemini 2.5 Flash, 1.5 Flash, or 1.5 Pro
- **🎨 Custom Styling** - Beautiful dark theme with gradient accents
- **🎭 Persona Customization** - Define AI roles and tone/style preferences
- **📄 Context Files** - Upload additional context documents (.txt, .md)
- **🔥 Creativity Control** - Adjust temperature for more creative or focused outputs
- **📚 Prompt History** - Keep track of your last 5 enhanced prompts
- **📥 Export Options** - Download enhanced prompts as markdown files
- **💡 Examples** - Built-in example prompts to get you started
- **📊 Input Statistics** - Character and word counts for your inputs
- **🔒 Secure** - API key management for local and cloud deployment

## 🚀 Quick Start

### Local Development

1. **Clone or download this repository**

2. **Install Python 3.11+** (if not already installed)

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your API key**
   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a `.env` file in the project root:
     ```
     GEMINI_API_KEY="your_actual_api_key_here"
     ```

6. **Run the app**
   ```bash
   streamlit run app.py
   ```

7. **Open your browser** to http://localhost:8501

## ☁️ Deploy to Streamlit Cloud

1. **Push your code to GitHub**
   - Make sure `.env` is in `.gitignore` (already configured)
   - Don't commit your API key to GitHub!

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**

3. **Create a new app**
   - Connect your GitHub repository
   - Select the branch and set `app.py` as the main file

4. **Add your API key to Secrets**
   - In your app settings, go to "Secrets"
   - Add:
     ```toml
     GEMINI_API_KEY = "your_actual_api_key_here"
     ```

5. **Deploy!** 🎉

## 📖 How to Use

1. **Configure Settings** (in sidebar)
   - Select your preferred Gemini model
   - Adjust creativity level (temperature)
   - Define AI persona and tone

2. **Enter Your Raw Prompt**
   - Type or paste your unstructured prompt
   - Optionally upload a context file for additional information

3. **Generate**
   - Click "Generate Enhanced Prompt"
   - Wait for the AI to process (usually 2-5 seconds)

4. **Use Your Output**
   - Copy or download the enhanced prompt
   - View your prompt history
   - Generate variations with different settings

## 💡 Example Use Cases

- **Marketing Content** - Transform brief ideas into compelling copy
- **Technical Documentation** - Structure API docs and guides
- **Social Media Posts** - Create engaging LinkedIn/Twitter content
- **Email Templates** - Draft professional business communications
- **Blog Outlines** - Structure content with proper headings
- **Product Descriptions** - Write detailed, persuasive descriptions

## 🔧 Configuration Files

- **`.env`** - Local API key storage (gitignored)
- **`.streamlit/config.toml`** - Streamlit theme and server settings
- **`.streamlit/secrets.toml`** - Cloud deployment secrets (gitignored)
- **`requirements.txt`** - Python dependencies with pinned versions
- **`.gitignore`** - Excludes sensitive files from version control

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** - Web framework
- **[Google Gemini API](https://ai.google.dev/)** - AI language models
- **[Python 3.11+](https://www.python.org/)** - Programming language
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment management

## 📝 Project Structure

```
upe_tool/
├── app.py                          # Main application
├── .env                            # Local environment variables (gitignored)
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git exclusions
├── .streamlit/
│   ├── config.toml                 # Streamlit configuration
│   └── secrets.toml.example        # Secrets template
└── README.md                       # This file
```

## 🐛 Troubleshooting

### "API Key Missing or Invalid"
- **Local**: Check your `.env` file has the correct key
- **Cloud**: Verify secrets are configured in deployment settings

### "Module not found" errors
- Run `pip install -r requirements.txt` to install dependencies

### App won't start
- Ensure Python 3.11+ is installed: `python --version`
- Check all files are in the correct locations
- Review console output for specific error messages

### Slow generation
- Try switching to a faster model (Gemini 1.5 Flash)
- Lower the creativity/temperature setting
- Check your internet connection

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Inspired by the NetworkChuck Fabric concept

---

**Made with ❤️ for better prompting**
