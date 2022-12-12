from functions import *


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Arch")

    # Uncomment worldwide arch mirror
    with open("/tmp/arch/etc/pacman.d/mirrorlist", "r") as read:
        mirrors = read.readlines()
    # Uncomment first worldwide mirror
    mirrors[6] = mirrors[6][1:]
    with open("/tmp/arch/etc/pacman.d/mirrorlist", "w") as write:
        write.writelines(mirrors)

    # Apply temporary fix for pacman
    bash("mount --bind /tmp/arch /tmp/arch")
    with open("/tmp/arch/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # temporarily comment out CheckSpace, coz Pacman fails to check available storage space when run from a chroot
    temp_pacman[34] = f"#{temp_pacman[34]}"
    with open("/tmp/arch/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    print_status("Preparing pacman")
    chroot("pacman-key --init")
    chroot("pacman-key --populate archlinux")
    chroot("pacman -Syyu --noconfirm")  # update the whole system

    print_status("Installing packages")
    start_progress()  # start fake progress
    chroot("pacman -S --noconfirm base base-devel nano networkmanager xkeyboard-config linux-firmware sudo bluez "
           "bluez-utils")
    chroot("pacman -S --noconfirm git cloud-utils rsync flashrom parted")  # postinstall script dependencies

    # Preinstall cgpt and vboot-utils
    urlretrieve("https://github.com/eupnea-linux/arch-packages/releases/latest/download/vboot-cgpt-utils.pkg.tar.zst",
                filename="/tmp/arch/opt/vboot-cgpt-utils.pkg.tar.zst")
    # Install package
    chroot("pacman --noconfirm -U /opt/vboot-cgpt-utils.pkg.tar.zst")

    # Delete package tar
    rmfile("/tmp/arch/opt/vboot-cgpt-utils.pkg.tar.zst")

    stop_progress()  # stop fake progress

    print_status("Downloading and installing de, might take a while")
    start_progress()  # start fake progress
    print_status("Installing GNOME")
    chroot("pacman -S --noconfirm gnome gnome-extra gnome-initial-setup")
    chroot("systemctl enable gdm.service")

    stop_progress()  # stop fake progress
    print_status("Desktop environment setup complete")

    # enable networkmanager systemd service
    chroot("systemctl enable NetworkManager.service")
    # Enable bluetooth systemd service
    chroot("systemctl enable bluetooth")

    # Configure sudo
    with open("/tmp/arch/etc/sudoers", "r") as conf:
        temp_sudoers = conf.readlines()
    # uncomment wheel group
    temp_sudoers[84] = temp_sudoers[84][2:]
    with open("/tmp/arch/etc/sudoers", "w") as conf:
        conf.writelines(temp_sudoers)

    print_status("Restoring pacman config")
    with open("/tmp/arch/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # comment out CheckSpace
    temp_pacman[34] = temp_pacman[34][1:]
    with open("/tmp/arch/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)


# using arch-chroot for arch
def chroot(command: str):
    if verbose:
        bash(f'arch-chroot /tmp/arch bash -c "{command}"')
    else:
        bash(f'arch-chroot /tmp/arch bash -c "{command}"')  # supress all output
