# Willmann modes

Here all modes will be collected for [willmann](https://github.com/aotabekov91/willmann).

## Install

To install, for example, a keyboard mode.

```bash
# Copy all modes
mkdir /tmp/modes
cd /tmp/modes
git clone https://github.com/aotabekov91/willmann_modes

cd willmann_modes/modes/keyboard
# Install required packages for the mode
pip install -r requirements.txt

# Copy the mode to the willman modes folder
cd .. 
cp -r keyboard $HOME/.config/willmann/modes

# Remove temporary files
rm -rf /tmp/modes

# !Enable keyboard mode
# vim $HOME/.config/willmann/config.ini
# modes_include= ..., keyboard

# Reload willmann
killall willmann
willmann
```

## Usage

### Run an application

### Look up a definition 

### Change keyboard layout

### Player control

### Bookmark create/search

### Etc.

## How to extend [i.e., creating a new mode]

Have a look at the [samples](https://github.com/aotabekov91/willmann/samples).
