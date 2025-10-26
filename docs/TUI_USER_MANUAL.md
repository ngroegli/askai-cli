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

### Tabbed Interface
When you launch the TUI, you'll see a modern tabbed interface with five main tabs:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Question Builder | Pattern Browser | Chat Browser | Model Browser | Credits │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Current tab content displayed here]                                   │
│                                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
 F1 Help  F2 Question  F3 Patterns  F4 Chats  F5 Models  F6 Credits  ^Q Quit
```

### Global Navigation
These shortcuts work from any tab:

| Shortcut | Action | Description |
|----------|--------|-------------|
| `F1` | Help | Show context-sensitive help |
| `F2` | Question Tab | Switch to Question Builder |
| `F3` | Patterns Tab | Switch to Pattern Browser |
| `F4` | Chats Tab | Switch to Chat Browser |
| `F5` | Models Tab | Switch to Model Browser |
| `F6` | Credits Tab | Switch to Credits Monitor |
| `Ctrl+Q` | Quit Application | Exit TUI completely |

## Question Builder Tab

### Interface Layout
The Question Builder uses a two-panel layout:

```
┌─── Question Input Panel ───┐ ┌─── Answer Display Panel ───┐
│ Question:                  │ │ Answer                      │
│ ┌────────────────────────┐ │ │ ┌─────────────────────────┐ │
│ │ Enter your question    │ │ │ │ AI response appears     │ │
│ │ here...                │ │ │ │ here after execution    │ │
│ │                        │ │ │ │                         │ │
│ └────────────────────────┘ │ │ │                         │ │
│                            │ │ │                         │ │
│ [Ask AI] [Clear]           │ │ │                         │ │
│                            │ │ │                         │ │
│ File: [optional]           │ │ │                         │ │
│ URL:  [optional]           │ │ │                         │ │
│ Format: [Text ▼]           │ │ │                         │ │
└────────────────────────────┘ └─────────────────────────────┘
```

### Using the Question Builder
1. **Enter Your Question**: Click in the text area and type your question
2. **Add Context (Optional)**:
## Model Browser Tab

### Interface Layout
The Model Browser displays live OpenRouter model data in a two-panel layout:

```
┌─── Model List Panel ──────┐ ┌─── Model Details Panel ────┐
│ 🔍 Search models...       │ │ Model: GPT-4               │
│                           │ │ Provider: OpenAI           │
│ ○ GPT-4 (OpenAI)         │ │ Context: 128k tokens       │
│ ● GPT-3.5 Turbo          │ │ Pricing: $0.01/1k tokens  │
│ ○ Claude-3 (Anthropic)   │ │                            │
│ ○ Gemini Pro (Google)    │ │ Capabilities:              │
│ ○ Mixtral (Mistral)      │ │ • Text generation          │
│ ○ Llama 2 (Meta)         │ │ • Code completion          │
│                           │ │ • Reasoning tasks          │
│ [Refresh Models]          │ │                            │
└───────────────────────────┘ └────────────────────────────┘
```

### Using the Model Browser
1. **Browse Models**: Scroll through available AI models
2. **Search/Filter**: Use search box to find specific models
3. **View Details**: Click a model to see pricing and capabilities
4. **Real-time Data**: Information updates automatically from OpenRouter

## Credits Tab

### Credit Monitoring Interface
```
┌─────────────── Credit Balance ────────────────┐
│                                               │
│  Total Credits: $60.00                        │
│  Used Credits:  $39.12                        │
│  Remaining:     $20.88                        │
│                                               │
│  ████████████████████████░░░░░░░░░ 65%        │
│                                               │
│  Usage History:                               │
│  • Question processing: $25.40                │
│  • Pattern execution:   $8.72                 │
│  • Model testing:       $5.00                 │
│                                               │
│  [Refresh Balance]                            │
└───────────────────────────────────────────────┘
```

### Credit Management
- **Real-time Balance**: Live credit information from OpenRouter API
- **Usage Tracking**: Monitor spending across different features
- **Visual Progress**: Progress bar shows credit consumption
- **Manual Refresh**: Update balance on demand

## Pattern Browser Tab

### Interface Layout
```
┌─── Pattern List Panel ────┐ ┌─── Pattern Details Panel ──┐
│ 🔍 Search patterns...     │ │ Pattern: Data Visualization │
│                           │ │ Category: Analysis          │
│ ○ Data Visualization      │ │ Description:                │
│ ● PDF Summary             │ │ Creates visual charts and   │
│ ○ Log Interpretation      │ │ graphs from data sources.   │
│ ○ Code Generation         │ │                             │
│ ○ Content Summary         │ │ Required Inputs:            │
│ ○ Market Analysis         │ │ • Data file or URL          │
│                           │ │ • Chart type preference     │
│ [Execute Pattern]         │ │ • Output format             │
└───────────────────────────┘ └─────────────────────────────┘
```

### Pattern Execution
1. **Browse Patterns**: View available AI patterns in the left panel
2. **Pattern Details**: Select a pattern to see requirements and description
3. **Execute**: Click "Execute Pattern" to launch the selected pattern
4. **Follow Prompts**: Pattern will guide you through required inputs
5. **View Results**: AI-generated content displays in the response area

## Chat Browser Tab

### Chat Management Interface
```
┌─── Chat Sessions Panel ───┐ ┌─── Chat Content Panel ─────┐
│ 🔍 Search chats...        │ │ Chat: Project Planning      │
│                           │ │ Created: 2024-01-15         │
│ ○ Project Planning        │ │                             │
│ ● API Design Discussion   │ │ You: How should I structure │
│ ○ Code Review Session     │ │      my REST API?           │
│ ○ Feature Requirements    │ │                             │
│ ○ Bug Investigation       │ │ AI: For a well-structured   │
│                           │ │     REST API, consider...   │
│ [New Chat] [Delete Chat]  │ │                             │
└───────────────────────────┘ └─────────────────────────────┘
```

### Chat Operations
- **Browse Sessions**: View all saved chat conversations
- **Search/Filter**: Find specific chats by content or date
- **View History**: Read previous conversations with AI
- **Continue Chats**: Resume existing conversations
- **Manage Sessions**: Create new chats or delete old ones

## Navigation and Shortcuts

### Tab Navigation
| Key Combination | Action | Description |
|----------------|--------|-------------|
| `Tab` | Next Tab | Move to the next tab |
| `Shift+Tab` | Previous Tab | Move to the previous tab |
| `Ctrl+1-5` | Direct Tab | Jump directly to tab number |

### Universal Shortcuts
| Key Combination | Action | Description |
|----------------|--------|-------------|
| `Ctrl+Q` | Quit | Exit the application |
| `Ctrl+R` | Refresh | Refresh current tab content |
| `F1` | Help | Show context-sensitive help |
| `Escape` | Cancel | Cancel current operation |

### Panel Navigation
| Key Combination | Action | Description |
|----------------|--------|-------------|
| `Ctrl+Left/Right` | Switch Panels | Move between left/right panels |
| `Enter` | Select/Execute | Activate selected item or button |
| `Space` | Toggle | Toggle selection where applicable |

## Troubleshooting

### Common Issues

#### Tab Content Not Loading
- **Symptom**: Empty or loading tab content
- **Solution**: Press `Ctrl+R` to refresh or check network connection
- **Prevention**: Ensure stable internet for OpenRouter API access

#### Input Fields Not Responding
- **Symptom**: Cannot type in question or search fields
- **Solution**: Click directly in the input area or press Tab to focus
- **Prevention**: Use Tab navigation to ensure proper field focus

#### Slow Model/Credit Updates
- **Symptom**: Outdated information in Model or Credits tabs
- **Solution**: Use refresh buttons or `Ctrl+R` to update
- **Prevention**: Check network connection quality

### Performance Tips
- Use search and filtering to reduce data loading
- Close unnecessary background applications
- Ensure adequate terminal size for proper layout
- Keep network connection stable for real-time updates

### Error Recovery
If the TUI encounters errors:
1. Try refreshing the current tab (`Ctrl+R`)
2. Switch to a different tab and return
3. Use `Escape` to cancel problematic operations
4. Restart the application if issues persist

## Advanced Usage

### Workflow Integration
The tabbed interface supports efficient workflows:
1. **Research Phase**: Use Model Browser to find optimal AI models
2. **Content Creation**: Execute questions or patterns based on research
3. **Iteration**: Review chat history to build on previous conversations
4. **Monitoring**: Track credit usage to manage costs

### Best Practices
- Keep the Credits tab visible to monitor usage
- Use descriptive chat names for better organization
- Leverage pattern templates for consistent results
- Bookmark frequently used models in your workflow

---

*For technical implementation details, see [TUI_ARCHITECTURE.md](TUI_ARCHITECTURE.md)*
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
