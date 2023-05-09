from capstone_checker import register_check, main, ValidationError
import subprocess

@register_check()
def check_command(context, args):
    print(context, args)
    command = args['command']
    p = subprocess.Popen(command, shell=True, cwd=context['app_dir'])
    p.wait(timeout=2)
    if p.returncode != 0:
        raise ValidationError(f"Command {command} failed with non-zero exit status. ({p.returncode})")


if __name__ == "__main__":
    main()
