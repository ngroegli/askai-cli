# TUI User Manual

## Getting Started with AskAI TUI

The AskAI Terminal User Interface (TUI) provides an interactive, visual way to work with AI-powered tools directly in your terminal. This modern interface offers intuitive navigation, real-time feedback, and streamlined workflows for all AskAI functionality.

## Launching the TUI

### Interactive Mode
```bash
# Launch interactive TUI interface
./askai.sh -i
# or
./askai.sh --interactive
```

### Environment Requirements
- **Terminal**: Modern terminal with 256-color support
- **Dependencies**: Textual framework (automatically installed)
- **Compatibility**: Linux, macOS, Windows (WSL supported)

### Fallback Behavior
If TUI is unavailable, AskAI automatically falls back to CLI mode with full functionality preserved.

## Main Interface

### Welcome Screen
When you launch the TUI, you'll see the main workflow selection screen:

```
🤖 AskAI Interactive Terminal
Choose your workflow to get started

🤔 Question Logic
Build interactive AI queries with context files, URLs, images, and PDFs
[Start Question Builder]

📋 Pattern Logic  
Browse patterns, preview markdown content, and execute with custom inputs
[Browse Patterns]

⚙️ System Management
Manage OpenRouter account, configuration, and system operations
[Open Internals]
```

### Global Navigation
These shortcuts work from any screen:

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+B` | Back to Main Menu | Return to workflow selection |
| `Ctrl+Q` | Quit Application | Exit TUI completely |
| `F1` | Help | Show context-sensitive help |
| `Esc` | Cancel/Back | Cancel current operation |

## Question Logic Workflow

### Starting Question Builder
1. From the main menu, click **"Start Question Builder"** or press **1**
2. The question input screen opens with a text area for your query

### Question Input Interface
```
┌─ Question Builder ────────────────────────────────────────┐
│                                                           │
│ Enter your question or prompt:                            │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ What is the best way to implement error handling    │   │
│ │ in Python applications?                             │   │
│ │                                                     │   │
│ │                                                     │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                           │
│ [Execute Question]  [Clear]  [Back to Main Menu]         │
│                                                           │
│ Status: Ready to execute                                  │
└───────────────────────────────────────────────────────────┘
```

### Question Workflow Steps
1. **Input**: Type your question in the text area
2. **Execute**: Click "Execute Question" or press `Ctrl+R`
3. **Loading**: Animated loading screen shows progress
4. **Response**: AI response opens in dedicated viewer
5. **Actions**: Choose next action (new question, back to menu, etc.)

### Question Builder Shortcuts
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+R` | Execute Question | Process current question |
| `Ctrl+N` | New Question | Clear form for new question |
| `Tab` | Navigate Fields | Move between input elements |

### Context and File Support
The question builder supports various context types:
- **Text Files**: Drag and drop or browse to attach
- **URLs**: Paste web URLs for content extraction
- **Images**: Upload images for visual analysis
- **PDFs**: Attach PDF documents for content analysis

## Pattern Logic Workflow

### Pattern Browser Interface
```
┌─ Pattern Browser ─────────────────────────────────────────┐
│ Search: [data visualization        ] 🔍                   │
├─────────────────────────┬─────────────────────────────────┤
│ Pattern List            │ Preview Pane                    │
│                         │                                 │
│ ▶ Data Visualization    │ # Data Visualization Pattern    │
│   Web Development       │                                 │
│   Code Generation       │ Create interactive charts and   │
│   Log Analysis          │ graphs from datasets using      │
│   Market Research       │ modern visualization libraries. │
│                         │                                 │
│ [Use Pattern]           │ ## Features                     │
│                         │ - Multiple chart types         │
│                         │ - Interactive legends          │
│                         │ - Export capabilities           │
└─────────────────────────┴─────────────────────────────────┘
```

### Pattern Workflow Steps
1. **Browse**: View available patterns in the left panel
2. **Search**: Use the search box to filter patterns
3. **Preview**: Select a pattern to see preview in right panel
4. **Configure**: Set pattern-specific inputs and parameters
5. **Execute**: Run the pattern with your configuration
6. **Results**: View formatted output and export options

### Pattern Browser Shortcuts
| Shortcut | Action | Description |
|----------|--------|-------------|
| `/` | Focus Search | Quick search activation |
| `Enter` | Select Pattern | Choose highlighted pattern |
| `Ctrl+P` | Toggle Preview | Show/hide preview pane |
| `↑/↓` | Navigate List | Move through pattern list |

### Pattern Types
- **Data Visualization**: Create charts and graphs from data
- **Code Generation**: Generate code in various languages
- **Content Creation**: Write articles, documentation, etc.
- **Analysis Tools**: Log analysis, market research, etc.
- **System Commands**: Linux CLI command generation

## System Management Workflow

### System Dashboard
Access system-level functionality including:
- **Configuration Management**: Edit settings and preferences
- **API Key Management**: Configure OpenRouter and other API keys
- **Logs and Monitoring**: View application logs and health status
- **Pattern Management**: Create, edit, and manage custom patterns

### Configuration Interface
```
┌─ System Configuration ────────────────────────────────────┐
│                                                           │
│ OpenRouter API Settings                                   │
│ API Key: [****************************] [Test Connection] │
│ Model: [gpt-4] ▼                                         │
│                                                           │
│ TUI Preferences                                           │
│ Theme: [Dark] ▼                                          │
│ Animation: [Enabled] ☑                                   │
│ Sound: [Disabled] ☐                                      │
│                                                           │
│ [Save Settings]  [Reset to Defaults]  [Export Config]    │
└───────────────────────────────────────────────────────────┘
```

## Response Viewer

### Response Display Features
```
┌─ AI Response ─────────────────────────────────────────────┐
│                                                           │
│ Python Error Handling Best Practices                     │
│ ═══════════════════════════════════════                   │
│                                                           │
│ Here are the key strategies for effective error          │
│ handling in Python applications:                         │
│                                                           │
│ ## 1. Use Specific Exception Types                       │
│ ```python                                                │
│ try:                                                      │
│     value = int(user_input)                              │
│ except ValueError as e:                                   │
│     print(f"Invalid number: {e}")                        │
│ ```                                                       │
│                                                           │
│ [Ask Another Question]  [Back to Main Menu]  [Copy Text] │
└───────────────────────────────────────────────────────────┘
```

### Response Actions
- **Ask Another Question**: Clear form and start new question
- **Back to Main Menu**: Return to workflow selection
- **Copy Text**: Copy response to clipboard
- **Save Response**: Export response to file
- **Share Response**: Generate shareable link

### Response Navigation
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | New Question | Start another question |
| `Ctrl+C` | Copy Response | Copy to clipboard |
| `Ctrl+S` | Save Response | Save to file |
| `Page Up/Down` | Scroll | Navigate long responses |

## Advanced Features

### Multi-Context Questions
Combine multiple context sources in a single question:
1. **Files**: Attach relevant documentation or code files
2. **URLs**: Include web pages for current information
3. **Images**: Add screenshots or diagrams for visual context
4. **Previous Responses**: Reference earlier AI responses

### Pattern Customization
Create and modify patterns for repeated tasks:
1. **Pattern Templates**: Markdown-based pattern definitions
2. **Variable Substitution**: Dynamic content insertion
3. **Custom Instructions**: Specialized AI prompts
4. **Output Formatting**: Structured response templates

### Search and Filtering
- **Pattern Search**: Full-text search across pattern library
- **Category Filtering**: Browse patterns by type or domain
- **Recent Items**: Quick access to recently used patterns
- **Favorites**: Save frequently used patterns for quick access

## Troubleshooting

### Common Issues

#### TUI Won't Start
```bash
# Check terminal compatibility
echo $TERM

# Verify Python environment
python --version

# Test Textual installation
python -c "import textual; print('TUI available')"
```

#### Display Issues
- **Colors**: Ensure terminal supports 256 colors
- **Size**: Minimum 80x24 terminal size recommended
- **Fonts**: Use monospace fonts for best experience

#### Performance Issues
- **Memory**: Close other terminal applications
- **Network**: Check internet connection for AI API calls
- **Processing**: Large files may require more time

### Getting Help

#### In-Application Help
- Press `F1` from any screen for context-sensitive help
- Use `Ctrl+?` for keyboard shortcut reference
- Check status messages for real-time guidance

#### External Resources
- **Documentation**: Full docs in `docs/` directory
- **Issues**: Report bugs on project GitHub
- **Community**: Join discussions and get support

## Keyboard Reference

### Global Shortcuts (Work Everywhere)
```
Ctrl+B     Back to Main Menu
Ctrl+Q     Quit Application
F1         Context Help
Esc        Cancel/Back
Tab        Next Field
Shift+Tab  Previous Field
```

### Question Builder
```
Ctrl+R     Execute Question
Ctrl+N     New Question
Ctrl+L     Clear Form
Ctrl+F     Attach File
```

### Pattern Browser
```
/          Focus Search
Enter      Select Pattern
Ctrl+P     Toggle Preview
↑/↓        Navigate List
Ctrl+E     Edit Pattern
```

### Response Viewer
```
Ctrl+N     New Question
Ctrl+C     Copy Response
Ctrl+S     Save Response
Page Up    Scroll Up
Page Down  Scroll Down
```

### System Management
```
Ctrl+S     Save Settings
Ctrl+T     Test Connection
Ctrl+L     View Logs
Ctrl+R     Refresh Status
```

## Tips and Best Practices

### Efficient Workflow
1. **Use Shortcuts**: Learn keyboard shortcuts for faster navigation
2. **Pattern Library**: Leverage patterns for repeated tasks
3. **Context Files**: Attach relevant files for better AI responses
4. **Save Responses**: Export important responses for future reference

### Question Optimization
- **Be Specific**: Clear, detailed questions get better responses
- **Provide Context**: Include relevant background information
- **Use Examples**: Show examples of desired output format
- **Iterate**: Refine questions based on initial responses

### Pattern Usage
- **Browse First**: Explore available patterns before creating new ones
- **Customize**: Modify existing patterns for specific needs
- **Document**: Add clear descriptions to custom patterns
- **Test**: Validate patterns with sample inputs

### System Maintenance
- **Regular Updates**: Keep dependencies updated
- **Monitor Usage**: Check API usage and limits
- **Backup Config**: Export settings before major changes
- **Clean Logs**: Periodically clear old log files

## Conclusion

The AskAI TUI provides a powerful, intuitive interface for AI-powered workflows. With its keyboard-driven navigation, visual feedback, and integrated tools, it streamlines complex AI interactions into simple, efficient workflows.

Whether you're asking questions, using patterns, or managing system settings, the TUI offers a modern, accessible way to harness AI capabilities directly from your terminal.

For additional help or advanced usage scenarios, refer to the comprehensive documentation in the `docs/` directory or use the built-in help system accessible via `F1` from any screen.
