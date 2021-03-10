#!/bin/sh
echo "This script uses sudo. You'll probably need to enter your password."
sudo pkgbuild --identifier com.github.jc0b.enable_arm64_scripting --root payload/ --scripts /Users/jc0b/Desktop/enable_zuludesk_scripting_arm64/scripts "Install Rosetta and start LaunchDaemons.pkg"
sudo productbuild --package Install\ Rosetta\ and\ start\ LaunchDaemons.pkg Install\ Rosetta\ and\ Restart\ LDs\ product.pkg