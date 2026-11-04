from bankapp.cli import ConsoleApp
from bankapp.service import seed_demo


def run(service, inputs, secrets):
    inputs, secrets, out = iter(inputs), iter(secrets), []

    def reader(source):
        def read(_prompt):
            try:
                return next(source)
            except StopIteration:
                raise EOFError from None

        return read

    app = ConsoleApp(
        service,
        input_fn=reader(inputs),
        secret_fn=reader(secrets),
        output=out.append,
    )
    app.run()
    return "\n".join(out)


def test_register_then_login_and_deposit(service):
    output = run(
        service,
        # register: name, username, type, deposit | login: username | session: deposit, amount
        ["1", "Carol King", "carol", "2", "50", "2", "carol", "2", "$25", "8", "3"],
        ["4321", "4321", "4321"],
    )
    assert "Your account number is #000001" in output
    assert "Welcome back, Carol King!" in output
    assert "Deposited $25.00. New balance: $75.00" in output


def test_errors_are_shown_not_raised(service):
    seed_demo(service)
    output = run(
        service,
        # login bob, withdraw too much, transfer to missing account, log out, exit
        ["2", "bob", "3", "1000", "4", "999", "5", "8", "3"],
        ["5678"],
    )
    assert "Insufficient funds. You can withdraw up to $350.00." in output
    assert "Destination account #000999 not found." in output
    assert "Goodbye, Bob Jones!" in output


def test_eof_exits_cleanly(service):
    output = run(service, [], [])
    assert "Goodbye!" in output
