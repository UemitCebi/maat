package maat

import (
	"errors"
	"fmt"

	"github.com/charmbracelet/huh"
)

// wizardResult is what runInitWizard collects. ok is false (with a nil
// error) when the user aborts the form (Ctrl-C/Esc) rather than submits it.
type wizardResult struct {
	name    string
	summary string
	ok      bool
}

// runInitWizard prompts interactively for the project name and summary that
// --name/--summary would otherwise supply. It is a var so tests can inject
// a canned result without driving a real terminal UI.
var runInitWizard = func(defaultName string) (wizardResult, error) {
	var name, summary string
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewInput().
				Title("Project name").
				Placeholder(defaultName).
				Value(&name),
			huh.NewText().
				Title("One-line summary").
				Placeholder("TODO: one-paragraph description of this project.").
				Value(&summary),
		),
	).WithTheme(huh.ThemeCharm())

	if err := runForm(form); err != nil {
		if errors.Is(err, huh.ErrUserAborted) {
			return wizardResult{}, nil
		}
		// A misbehaving terminal (unusual multiplexer, a Bubble Tea/Huh
		// rendering bug triggered by an edge-case window size, ...) must not
		// take `init` down with it. Fall back to the same defaults the
		// non-interactive path would have used.
		return wizardResult{name: defaultName, ok: true}, nil
	}

	if name == "" {
		name = defaultName
	}
	return wizardResult{name: name, summary: summary, ok: true}, nil
}

// runForm isolates form.Run() behind a recover(): Huh v1.0.0 has at least
// one known path (checking the returned tea.Model before checking the
// error) where an underlying Bubble Tea failure surfaces as a panic instead
// of an error. See ADR 0011 / the presentation module doc.
func runForm(form *huh.Form) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("interactive wizard failed: %v", r)
		}
	}()
	return form.Run()
}
