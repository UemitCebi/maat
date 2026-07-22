package maat

import (
	"io"
	"os"

	"github.com/mattn/go-isatty"
)

// isInteractiveTerminal reports whether stdout and stdin are both attached
// to a real terminal. It gates the init wizard (cmdInit): Huh reads
// keystrokes from stdin, so a real terminal on stdout with piped/redirected
// stdin must not launch a form. Tests call Main with *bytes.Buffer, which
// never satisfies the *os.File assertion, so this seam is unreachable from
// the existing test suite without overriding it.
var isInteractiveTerminal = func(stdout io.Writer) bool {
	f, ok := stdout.(*os.File)
	if !ok {
		return false
	}
	return isatty.IsTerminal(f.Fd()) && isatty.IsTerminal(os.Stdin.Fd())
}
