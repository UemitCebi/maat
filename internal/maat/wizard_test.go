package maat

import (
	"io"
	"strings"
	"testing"
)

// --------------------------------------------------------------------------- #
// init wizard trigger (interactive TTY + no --name/--summary)
// --------------------------------------------------------------------------- #

func TestCmdInitSkipsWizardWhenNotATTY(t *testing.T) {
	// No overrides at all: the run() helper's strings.Builder is never a
	// *os.File, so isInteractiveTerminal is false by construction — this
	// proves the wizard branch is unreachable from the existing test suite.
	root := t.TempDir()
	_, _, code := run(t, "init", root)
	if code != 0 {
		t.Fatalf("init exited %d", code)
	}
}

func TestCmdInitLaunchesWizardWhenInteractiveAndNoFlags(t *testing.T) {
	oldTTY, oldWizard := isInteractiveTerminal, runInitWizard
	defer func() { isInteractiveTerminal, runInitWizard = oldTTY, oldWizard }()

	isInteractiveTerminal = func(io.Writer) bool { return true }
	called := false
	runInitWizard = func(defaultName string) (wizardResult, error) {
		called = true
		return wizardResult{name: "Wizarded", summary: "from the wizard", ok: true}, nil
	}

	root := t.TempDir()
	_, _, code := run(t, "init", root)
	if code != 0 {
		t.Fatalf("init exited %d", code)
	}
	if !called {
		t.Fatal("expected runInitWizard to be called")
	}
	if !strings.Contains(readFile(t, root, "AGENTS.md"), "Wizarded") {
		t.Error("expected wizard-supplied name to reach the scaffold")
	}
}

func TestCmdInitSkipsWizardWhenFlagsGiven(t *testing.T) {
	oldTTY, oldWizard := isInteractiveTerminal, runInitWizard
	defer func() { isInteractiveTerminal, runInitWizard = oldTTY, oldWizard }()

	isInteractiveTerminal = func(io.Writer) bool { return true } // even though "interactive"...
	runInitWizard = func(defaultName string) (wizardResult, error) {
		t.Fatal("wizard must not be invoked when --name/--summary are given")
		return wizardResult{}, nil
	}

	root := t.TempDir()
	_, _, code := run(t, "init", root, "--name", "Flagged", "--summary", "from flags")
	if code != 0 {
		t.Fatalf("init exited %d", code)
	}
}

func TestCmdInitReturns130OnWizardAbort(t *testing.T) {
	oldTTY, oldWizard := isInteractiveTerminal, runInitWizard
	defer func() { isInteractiveTerminal, runInitWizard = oldTTY, oldWizard }()

	isInteractiveTerminal = func(io.Writer) bool { return true }
	runInitWizard = func(defaultName string) (wizardResult, error) {
		return wizardResult{ok: false}, nil
	}

	root := t.TempDir()
	_, _, code := run(t, "init", root)
	if code != 130 {
		t.Fatalf("expected exit code 130 on wizard abort, got %d", code)
	}
}

// --------------------------------------------------------------------------- #
// color styling seam
// --------------------------------------------------------------------------- #

func TestColorPathPreservesPlainText(t *testing.T) {
	oldColor := isColorEnabled
	defer func() { isColorEnabled = oldColor }()
	isColorEnabled = func(io.Writer) bool { return true }

	root := t.TempDir()
	out, _, code := run(t, "init", root, "--name", "X", "--summary", "Y")
	if code != 0 {
		t.Fatalf("init exited %d", code)
	}
	if !strings.Contains(out, "\x1b[") {
		t.Error("expected ANSI escape codes when color is forced on")
	}
	plain := stripANSI(out)
	if !strings.Contains(plain, "  create  ") {
		t.Errorf("stripped output should still read like the plain path, got: %q", plain)
	}
}

func TestCheckColorPathIsNeverAppliedToGitHubFormat(t *testing.T) {
	oldColor := isColorEnabled
	defer func() { isColorEnabled = oldColor }()
	isColorEnabled = func(io.Writer) bool { return true }

	root := initRepo(t)
	out, _, _ := run(t, "check", root, "--format", "github")
	if strings.Contains(out, "\x1b[") {
		t.Error("--format=github output must never contain ANSI escape codes")
	}
}

func stripANSI(s string) string {
	var b strings.Builder
	inEscape := false
	for _, r := range s {
		switch {
		case r == '\x1b':
			inEscape = true
		case inEscape && r == 'm':
			inEscape = false
		case !inEscape:
			b.WriteRune(r)
		}
	}
	return b.String()
}
