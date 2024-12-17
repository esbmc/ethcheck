import importlib.resources

forks = ['altair', 'bellatrix', 'electra', 'phase0', 'phase1', 'deneb', 'capella']

def list_forks():
    try:
        package = importlib.resources.files("eth2spec")
        # List directories available in the 'eth2spec' package
        available_dirs = [item.name for item in package.iterdir() if item.is_dir()]
        # Return only the directories that are present in the 'forks' list
        return sorted(set(available_dirs).intersection(forks))
    except ModuleNotFoundError:
        print("Package 'eth2spec' not found.")
        return []

if __name__ == "__main__":
    dirs = list_forks()
    print(dirs)

