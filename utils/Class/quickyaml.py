class quickyaml:
    """
    A class to handle YAML files with a simple interface.
    """

    def __init__(self, filename: str):
        """
        Initialize the QuickYaml object with a filename.

        :param filename: The name of the YAML file to read.
        """
        self.filename = filename

    def __modify__(self, keyname: str, values: list):
        """
        Modify the YAML file by adding or updating a key with a list of values.

        :param keyname: The key to modify in the YAML file.
        :param values: The list of values to set for the key.
        """
        if not hasattr(self, 'data'):
            self.load()

        if keyname in self.data:
            self.data[keyname] = values
        else:
            self.data[keyname] = values

        self.save()
        print(f"Modified {keyname} in {self.filename}")

    def load(self):
        """
        Load the YAML file and parse its content.
        """
        import yaml

        with open(self.filename, 'r') as file:
            self.data = yaml.safe_load(file)

    def save(self):
        """
        Save the current data to the YAML file.
        """
        import yaml

        with open(self.filename, 'w') as file:
            yaml.dump(self.data, file)
        print(f"Data saved to {self.filename}")