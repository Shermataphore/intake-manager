# Manifest Manager

**Manifest Manager** is a Python GUI application that helps bring in products from Dutchie that have been accepted on Metrc.

## Overview

This tool opens in a new window and provides three tabs:

1. **Active Manifest**

   * Clones what is on the "Receive Inventory" page for Dutchie.

2. **Vendor Products**

   * Allows you to look up products by Dutchie vendor name so you can edit the vendor's products that are imported automatically.

3. **Metrc / Dutchie Vendor Name**

   * Provides a direct mapping between the names brought in under Metrc (input) and the corresponding Dutchie names (output).

## Installation

1. Ensure you have Python 3.x installed.
2. Install dependencies:

   ```bash
   pip install PyQt5
   ```

## Usage

1. Clone this repository:

   ```bash
   git clone https://github.com/Shermataphore/intake-manager.git
   cd intake-manager
   ```
2. Create a `.env` file with the environment variables used in
   `secrets.py` (for example `USERNAME` and `PASSWORD`).

3. Run the application:

   ```bash
   python main.py
   ```

## License

Specify your license here.

no license
