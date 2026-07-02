// Command codedoc is the CodeDoc CLI: documentation-as-code for humans and AI
// agents. It scaffolds (init), regenerates derived artifacts (sync), and
// validates the docs set as a CI gate (check).
package main

import (
	"os"

	"codedoc/internal/codedoc"
)

func main() {
	os.Exit(codedoc.Main(os.Args[1:], os.Stdout, os.Stderr))
}
