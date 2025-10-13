using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using System.Globalization;
using System.Text;
using System.Text.Json;

namespace Labs.Shared.Utils
{
    /// <summary>
    /// Elegant console narrator for Sentra Labs demos.
    /// Handles structured and streaming output with color and pacing.
    /// </summary>
    public static class Echo
    {
        // === Public API ===
        public static void System(string text, bool nl = true) => Write("⚙ :", text, ConsoleColor.DarkGray, nl);
        public static void Info(string text, bool nl = true) => Write("ℹ :", text, ConsoleColor.Cyan, nl);
        public static void User(string text, bool nl = true) => Write("🧑:", text, ConsoleColor.Yellow, nl);
        public static void Agent(string text, bool nl = true) => Write("🤖:", text, ConsoleColor.Green, nl);
        public static void Warn(string text, bool nl = true) => Write("⚠:", text, ConsoleColor.Magenta, nl);
        public static void Step(string text, bool nl = true) => Write("✔:", text, ConsoleColor.DarkYellow, nl);
        public static void Error(string text, bool nl = true) => Write("⛔:", text, ConsoleColor.Red, nl);
        public static void Done(string text, bool nl = true) => Write("✅:", text, ConsoleColor.Cyan, nl);

        /// <summary>
        /// Streams an agent run and narrates each content type appropriately.
        /// Handles text, reasoning, tool calls, tool results, and unknown items.
        /// </summary>
        public static async Task StreamAgentAsync(IAsyncEnumerable<AgentRunResponseUpdate> updates)
        {
            bool inAgentLine = false;

            await foreach (var update in updates)
            {
              
                if (!string.IsNullOrEmpty(update.Text))
                {
                    if (!inAgentLine)
                    {
                        Console.ResetColor();
                        Console.ForegroundColor = ConsoleColor.Green;
                        Console.Write("🤖: ");
                        inAgentLine = true;
                    }
                    Console.Write(update.Text);
                    continue;
                }

                if (update.Contents is not { Count: > 0 })
                    continue;

                if (inAgentLine)
                {
                    Console.WriteLine();
                    Console.ResetColor();
                    inAgentLine = false;
                }

                foreach (var content in update.Contents)
                {
                    Console.ResetColor();   
                    switch (content)
                    {
                        case TextReasoningContent reasoning:
                            Step($"[THINK] {reasoning.Text}");
                            break;
                        case FunctionCallContent call:
                            string argText = call.Arguments is null
                                ? ""
                                : string.Join(" ",
                                    call.Arguments.Select(kv => $"{kv.Key}={FormatArg(kv.Value)}"));
                            Step($"[ACT] {call.Name} {argText}");
                            break;
                        case FunctionResultContent result:
                            string preview = ToPreview(result.Result);
                            System($"[TOOL] {result.CallId} → {preview}");
                            break;
                        case TextContent text:
                            Agent(text.Text);
                            break;
                        default:                           
                            break;
                    }
                }
            }

            if (inAgentLine)
            {
                Console.WriteLine();
                Console.ResetColor();
            }
        }



        private static void Write(string symbol, string msg, ConsoleColor color, bool nl)
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.ForegroundColor = color;
            Console.Write($"{symbol} ");
            if (nl) Console.WriteLine(msg);
            else Console.Write(msg);
            Console.ResetColor();
        }

        public static void Divider(char c = '─', int len = 60)
        {
            Console.ForegroundColor = ConsoleColor.DarkGray;
            Console.WriteLine(new string(c, len));
            Console.ResetColor();
        }

        private static string FormatArg(object? value)
        {
            if (value is null) return "null";
            return value switch
            {
                string s => s,
                bool b => b.ToString().ToLowerInvariant(),
                int or long or double or float or decimal =>
                    Convert.ToString(value, CultureInfo.InvariantCulture) ?? "",
                _ => JsonSerializer.Serialize(value)
            };
        }

        private static string ToPreview(object? resultObj, int max = 240)
        {
            if (resultObj is null) return "(null)";
            string s = resultObj switch
            {
                string str => str,
                BinaryData bd => bd.ToString(),
                _ => JsonSerializer.Serialize(resultObj)
            };
            return s.Length > max ? s[..max] + "…" : s;
        }
    }
}