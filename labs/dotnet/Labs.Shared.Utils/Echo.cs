using Microsoft.Agents.AI;
using System.Text;

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
        public static void Error(string text, bool nl = true) => Write("⛔:", text, ConsoleColor.Red, nl);
        public static void Done(string text, bool nl = true) => Write("✅:", text, ConsoleColor.Cyan, nl);

        /// <summary>
        /// Streams agent output token by token, keeping formatting clean.
        /// </summary>
        public static async Task StreamAgentAsync(IAsyncEnumerable<AgentRunResponseUpdate> updates)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.Write("🤖: ");

            await foreach (var update in updates)
            {
                if (!string.IsNullOrEmpty(update.Text))
                    Console.Write(update.Text);
            }

            Console.WriteLine();
            Console.ResetColor();
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
    }
}
