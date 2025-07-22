This python script downloads, builds, and installs Open Stage Control on Apple Silicon Macs.

## Instructions

1. Download this repo or the [individual Python file](<./Open Stage Control - Apple Silicon installer.py>).
2. Open a new Terminal window and navigate to where you downloaded the aforementioned Python file. If you're unsure how to do this, follow the instructions on [this page](https://support.apple.com/guide/terminal/open-new-terminal-windows-and-tabs-trmlb20c7888/mac) under the section titled `Open new Terminal windows or tabs from the Finder`.
3. Type `python3 ./Open Stage Control - Apple Silicon installer.py`
4. A window requesting you to install the Xcode Command Line Tools may appear. If so, click `Install`. Once the installation is finished, repeat steps 2 and 3.

> [!NOTE]
>
> Note that you will only have to do this once -- subsequent executions of this script will not require you to install the Xcode Command Line Tools again.

5. A terminal window will appear -- wait for it to say that the process has completed, and then navigate to `/Applications/Open Stage Control` to run the newly-built app.
