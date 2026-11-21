# Bundle `relm-qa`

Target state for distributing the Relm qa setup as **one versioned unit** from the Relm private
catalog (Spec Kit bundles pin exact component versions and record provenance).

| Component | Version | Source |
|-----------|---------|--------|
| preset `relm-org` (priority 20) | 1.0.0 | relm catalog |
| preset `relm-qa` (priority 10) | 1.0.0 | relm catalog |
| extension `git` | 1.0.8 | Spec Kit |
| extension `github` | 1.0.6 | Spec Kit |
| extension `relm` | 1.0.0 | relm catalog |

Until the Relm bundle catalog is published, use the equivalent bootstrap script, which installs the
same components from a checkout of this repository:

```bash
bash ../speckit-platform/bootstrap/init-repo.sh qa
```
