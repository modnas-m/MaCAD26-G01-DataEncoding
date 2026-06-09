import sys
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

NB_PATH = 'notebooks/04_KMeans.ipynb'

def main():
    try:
        nb = nbformat.read(NB_PATH, as_version=4)
    except Exception as e:
        print(f'ERROR: failed to read notebook: {e}')
        sys.exit(2)

    try:
        kernel_name = nb.metadata.get('kernelspec', {}).get('name', 'python3')
        client = NotebookClient(nb, timeout=600, kernel_name=kernel_name)
        client.execute()
    except CellExecutionError as e:
        print('CELL-ERROR:')
        print(e)
        sys.exit(3)
    except Exception as e:
        print(f'EXECUTION-ERROR: {e}')
        sys.exit(4)

    # Report basic success summary
    executed = sum(1 for cell in nb.cells if cell.get('execution_count') is not None)
    total = len(nb.cells)
    print(f'EXECUTED: {executed}/{total} cells (in-memory, no file saved)')

if __name__ == '__main__':
    main()
