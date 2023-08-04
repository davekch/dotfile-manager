# file-dotfiles
to file your dotfiles

## usage
keep your dotfiles in this repository. for example
```text
.
├── .config
│  └── nvim
│     └── init.vim
├── .ssh
│  └── config
└── .zshrc
```

running `./install.py` will create symlinks to these files in your home directory, keeping the directory structure. for the example above, the script will create those links:
```text
$HOME/.zshrc -> /path/to/file-dotfiles/.zshrc
$HOME/.config/nvim/init.vim -> /path/to/file-dotfiles/testbed/.config/nvim/init.vim
$HOME/.ssh/config -> /path/to/file-dotfiles/testbed/.ssh/config
```

for extra fancyness, tag files or folders in the `dotfiles` section of `dotfile-config.yml` and specify combinations of tags to install. for example:
```yaml
dotfiles:
  .ssh/:
    tags: ssh
  .config/:
    tags: [config, blah]
  .config/gtk-3.0/gtk.css:
    tags: gui
  .zshrc:
    tags: zsh
```
now use `./install.py --tags config,ssh --skip-tags gui` to install every dot file in `.ssh` and `.config/` but not those that are tagged with `gui`.

all arguments:
```text
usage: install.py [-h] [--source SOURCE] [--target TARGET] [-f CONFIG_FILE] [--tags TAGS] [--skip-tags SKIP_TAGS] [-y] [--dry] [-v]

options:
  -h, --help            show this help message and exit
  --source SOURCE       directory of dotfiles (default='.')
  --target TARGET       home directory (defaul='~')
  -f CONFIG_FILE, --config-file CONFIG_FILE
                        path to config file
  --tags TAGS           specify tags to include. if no tags are given, everything is included
  --skip-tags SKIP_TAGS
                        specify tags to skip
  -y, --yes             don't ask to replace existing files
  --dry                 dry run (does not create or delete any files)
  -v                    verbose output
```