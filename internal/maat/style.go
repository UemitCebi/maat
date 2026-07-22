package maat

import (
	"fmt"
	"io"
	"os"

	"github.com/charmbracelet/lipgloss"
	"github.com/muesli/termenv"
)

// isColorEnabled reports whether output should carry ANSI styling. It is a
// separate, purely cosmetic gate from isInteractiveTerminal: NO_COLOR always
// wins, CLICOLOR_FORCE always forces color on, otherwise styling follows
// whether stdout is a real terminal. These two env vars affect only the
// ANSI escapes wrapped around otherwise-identical text — never validation
// results, exit codes, or file content — so they don't compromise
// reproducibility in CI (see docs/reference/environment.md).
var isColorEnabled = func(stdout io.Writer) bool {
	if os.Getenv("NO_COLOR") != "" {
		return false
	}
	if v := os.Getenv("CLICOLOR_FORCE"); v != "" && v != "0" {
		return true
	}
	return isInteractiveTerminal(stdout)
}

// styleRenderer always emits ANSI escapes. Call sites are the single
// source of truth for whether to use the styled render functions at all
// (via isColorEnabled) — this renderer must not second-guess that with its
// own terminal auto-detection, which would see the process's real stdout
// file descriptor (e.g. a test binary, never a terminal) and silently
// suppress color regardless of an isColorEnabled override.
var styleRenderer = func() *lipgloss.Renderer {
	r := lipgloss.NewRenderer(os.Stdout)
	r.SetColorProfile(termenv.ANSI)
	return r
}()

var (
	styleCreate  = styleRenderer.NewStyle().Foreground(lipgloss.Color("2"))
	styleSkip    = styleRenderer.NewStyle().Foreground(lipgloss.Color("3"))
	styleGen     = styleRenderer.NewStyle().Foreground(lipgloss.Color("6"))
	styleUpdate  = styleRenderer.NewStyle().Foreground(lipgloss.Color("6"))
	styleError   = styleRenderer.NewStyle().Foreground(lipgloss.Color("1")).Bold(true)
	styleWarn    = styleRenderer.NewStyle().Foreground(lipgloss.Color("3"))
	styleSuccess = styleRenderer.NewStyle().Foreground(lipgloss.Color("2")).Bold(true)
)

// The styled*Line helpers below mirror the plain fmt.Fprintf calls in
// cli.go byte-for-byte except for the ANSI escapes wrapped around the
// action word, so stripping color (NO_COLOR) reproduces the plain output
// exactly — no spacing or wording differs between the two paths.

func styledCreateLine(rel string) string {
	return fmt.Sprintf("  %s  %s", styleCreate.Render("create"), rel)
}

func styledSkipLine(rel string) string {
	return fmt.Sprintf("  %s    %s (exists; use --force to overwrite)", styleSkip.Render("skip"), rel)
}

func styledGenLine(rel string) string {
	return fmt.Sprintf("  %s     %s", styleGen.Render("gen"), rel)
}

func styledUpdateLine(rel string) string {
	return fmt.Sprintf("  %s  %s", styleUpdate.Render("update"), rel)
}

// styledFindingLine mirrors Finding.String() (check.go) exactly, styling
// only the severity icon. check.go itself is never modified: this keeps
// the machine-readable String() and the --format github path untouched.
func styledFindingLine(f Finding) string {
	icon, style := "⚠", styleWarn
	if f.Severity == "error" {
		icon, style = "✖", styleError
	}
	return fmt.Sprintf("%s [%s] %s: %s", style.Render(icon), f.Code, f.Where, f.Message)
}

func styledCheckSummary(total, errors, warnings int) string {
	counts := fmt.Sprintf("%d error(s), %d warning(s)", errors, warnings)
	if errors > 0 {
		counts = styleError.Render(counts)
	} else if warnings > 0 {
		counts = styleWarn.Render(counts)
	} else {
		counts = styleSuccess.Render(counts)
	}
	return fmt.Sprintf("\nChecked %d document(s): %s.\n", total, counts)
}
