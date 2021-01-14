# Adobe-CCDA
This folder contains a Munki `pre_uninstall` script for checking whether there are Adobe apps installed when removing the Adobe CC Desktop Application.

When providing a selfserve client to your users, Adobe notes that:
> "The Creative Cloud desktop app can only be uninstalled if all Creative Cloud apps (such as Photoshop, Illustrator, and Premiere Pro) have already been uninstalled from the system."

In order to prevent Munki from failing to remove the CC client, leaving it in a broken state, you can use this `pre_uninstall` script, which will fail if any Adobe CC apps remain on the system.

See [my blog post about this](https://jc0b.computer/posts/removing-adobe-cc-packages/) for more details.