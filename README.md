# Dotfile manager
A simple CLI tool to manage your dotfiles in a repository.

## Install
```bash
pip install git+https://github.com/davekch/dotfile-manager.git
```

## Usage
### Install dotfiles from a repository
Keep your dotfiles in a separate repository. For example
```text
dotfiles/
├── .config
│  └── nvim
│     └── init.vim
├── .ssh
│  └── config
└── .zshrc
```

running `dotfile init .` in it and then `dotfile install` will create symlinks to these files in your home directory, keeping the directory structure. For the example above, the command will create those links:
```text
$HOME/.zshrc -> /path/to/dotfiles/.zshrc
$HOME/.config/nvim/init.vim -> /path/to/dotfiles/.config/nvim/init.vim
$HOME/.ssh/config -> /path/to/dotfiles/.ssh/config
```

You can also selectively install dotfiles: `dotfile install .config`

### Adding dotfiles to the repository
`dotfile add file1 file2 ...` will copy the listed files to your repository and replace them with symlinks to the copied files in the repository.

### More
A configuration file is created in `~/.config/dotfile-manager/config.toml` when running `dofile init .`.

All options:
```
usage: dotfile [-h] [-v] {init,install,add} ...

positional arguments:
  {init,install,add}
    init              initialize dotfile manager
    install           create symlinks for dotfiles
    add               add files to the dotfile repository

options:
  -h, --help          show this help message and exit
  -v, --verbose       verbose output
```

```
usage: dotfile install [-h] [-e [EXCLUDE ...]] [--source SOURCE] [--target TARGET] [-y | -n] [--dry] [files ...]

positional arguments:
  files                 file paths relative to source to install. default is '.'

options:
  -h, --help            show this help message and exit
  -e [EXCLUDE ...], --exclude [EXCLUDE ...]
                        file paths relative to source not to install
  --source SOURCE       directory of dotfiles
  --target TARGET       home directory
  -y, --yes             always replace existing files
  -n, --no              never replace existing files
  --dry                 dry run (does not create or delete any files)
```

# Disclaimer
This tool moves and deletes files. Bugs can lead to loss of data. Use at your own risk.
