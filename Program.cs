// This app acts as a proxy app. The "Custom Launcher" calls this app with an argument.
// Args: days, recoded
// If "days" is passed, it will launch the Days executable.  If recoded is passed, it will launch the Recoded executable.
// it also attempts to launch WaitTitleProject.exe to wait for the selected game window and then terminating.

using System.Diagnostics;

class Program
{
    static void Main(string[] args)
    {
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        string argumentString = string.Join(" ", args).ToLowerInvariant();

        string targetExe = argumentString.Contains("recoded") ? "Recoded/recoded.exe" : "Days/khdays-native.exe";
        string exePath = Path.Combine(baseDir, targetExe);
        
        Process waitProcess = null;
        try
        {
            waitProcess = Process.Start(new ProcessStartInfo
            {
                FileName = Path.Combine(baseDir, "WaitTitleProject.exe"),
                Arguments = string.Join(" ", 1),
                WorkingDirectory = baseDir,
                UseShellExecute = false
            });
        }
        catch { }


        using (Process gameProcess = Process.Start(new ProcessStartInfo
               {
                   FileName = exePath,
                   WorkingDirectory = Path.GetDirectoryName(exePath),
                   UseShellExecute = false
               }))
        {
            if (gameProcess != null)
            {
                int timeoutMs = 15000;
                int elapsedMs = 0;
                while (elapsedMs < timeoutMs)
                {
                    gameProcess.Refresh();
                    if (gameProcess.MainWindowHandle != IntPtr.Zero || gameProcess.HasExited)
                        break;

                    Thread.Sleep(100);
                    elapsedMs += 100;
                }

                if (waitProcess != null && !waitProcess.HasExited)
                {
                    try
                    {
                        waitProcess.Kill();
                        waitProcess.Dispose();
                    }
                    catch { }
                }
            }
        }
    }
}