# Enable Zuludesk Scripting on Apple Silicon
This folder contains a means to create a package for Jamf School/Zuludesk, which will install Rosetta 2 on an Apple Silicon Mac. This allows the Jamf School scripting agent to run in cases where it is not a universal binary.
`sudo ./build.sh` will generate a regular .pkg, as well as a component/product .pkg that Jamf School will allow you to push via the `InstallApplication` MDM command, which doesn't require any MDM-specific binaries on the device. Once Rosetta has been installed, the scripting agent will automatically execute any pending scripts.

The contents in this folder are further explained in my [blog post on the subject](https://jc0b.computer/posts/jamf_school_scripting_on_apple_silicon/).