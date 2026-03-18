# slope-check

Audit AI papers, repos, and product pages against their quantitative claims.

"Slope" is the gap between what is promised and what is real.

## Install

```bash
claude plugin marketplace add kazakhpunk/slope-check
claude plugin install slope-check@kazakhpunk-slope-check
```

## Usage

```
/slope-check <url-or-path> [--run]
```

### Examples

```
# Audit a GitHub repo's README claims
/slope-check https://github.com/qdrant/fastembed

# Audit an arxiv paper
/slope-check https://arxiv.org/abs/2310.01469

# Audit both repo and paper together
/slope-check https://github.com/qdrant/fastembed https://arxiv.org/abs/2310.01469

# Include live benchmark replication attempt
/slope-check https://github.com/qdrant/fastembed --run
```

See [plugin/README.md](./plugin/README.md) for full documentation.
