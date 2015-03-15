## Why does ShellLogger change my prompt? ##

ShellLogger uses your prompt to determine what directory that you're currently in.

## ShellLogger isn't setting my prompt properly ##

Sometimes your prompt may be modified by some other Unix shell script. For example, if bash is your shell, check for modifications to the PS1 variable in:

  * .profile
  * .bash\_profile
  * .bash\_login
  * .login
  * .bashrc

Sometimes there are system-wide versions of these files (often in
/etc/skel) that are in effect.


## Why doesn't ShellLogger capture my input correctly when I use my arrow keys? ##

ShellLogger has some support for handling backspace properly, but it can't properly handle the case of using arrow-keys (e.g.  pushing the up arrow key to retrieve the previous command).