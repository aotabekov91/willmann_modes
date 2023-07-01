# Willmann modes

Here I will collect (almost) all modes for [willmann](https://github.com/aotabekov91/willmann).

## Install

To install, for example, a mode of keyboard.

```bash
# Copy all modes
mkdir tmp_willmann_modes
cd tmp_willmann_modes
git clone https://github.com/aotabekov91/willmann_modes

cd willmann_modes/modes/keyboard
# Install required packages for the mode
pip install -r requirements.txt

# Copy the mode to the willman modes folder
cp -r willmann_modes/modes/keyboard willmann/modes

# Reload willmann
killall willmann
python willmann/run.py
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
