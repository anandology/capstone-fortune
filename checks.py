from capstone_checker import register_check, main, ValidationError
import subprocess
from pathlib import Path
import shutil

def run_fortune(cwd):
    """Runs the fortune command.
    """
    command = "python fortune.py"
    p = subprocess.Popen(command, shell=True, cwd=cwd, text=True, stdout=subprocess.PIPE)
    p.wait(timeout=2)
    if p.returncode != 0:
        raise ValidationError(f"Command {command} failed with non-zero exit status. ({p.returncode})")
    return p.stdout.read().strip()

@register_check()
def check_fortune_working(context, args):
    run_fortune(cwd=context['app_dir'])

def parse_quotes(path):
    quotes = Path(path).read_text().split("%\n")
    return [q.strip() for q in quotes]

def prepare_files(app_dir):
    """Copy the fortune files to the app directory."""
    dest = Path(app_dir) / "files"
    src = Path(__file__).parent / "repo" / "files"

    print("prepating files...")

    for f in src.glob("*.txt"):
        p = dest / f.name
        shutil.copy(f, p)
        print(f"cp {f} {p}")

@register_check()
def check_fortune_is_from_file(context, args):
    root = context['app_dir']
    prepare_files(root)

    fortune_file = Path(root) / args.get("fortune_file", "files/fortune.txt")
    quotes = parse_quotes(fortune_file)
    output = run_fortune(cwd=root)
    if output not in quotes:
        raise ValidationError(
            "The program is expected to print a quote from the file," +
            " but what is printed is not from the fortune file." +
            "\n\n" +
            "OUTPUT OF THE PROGRAM:\n\n" +
            output +
            "\n\n" +
            "CONTENTS OF THE FORTUNE FILE:\n\n" +
            fortune_file.read())

@register_check()
def check_fortune_random(context, args):
    root = context['app_dir']
    prepare_files(root)

    fortune_file = Path(root) / "files" / "fortune.txt"
    quotes = parse_quotes(fortune_file)
    outputs = [run_fortune(cwd=root) for i in range(10)]
    if len(set(outputs)) == 1:
        raise ValidationError(
            "It is expected that the program will pick a quote at random," +
            " but it seems to be printing the same quote everytime." +
            "\n\n" +
            "OUTPUT OF THE PROGRAM (over 10 runs):\n" +
            outputs[0]
        )

if __name__ == "__main__":
    main()
