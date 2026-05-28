# GitLab Issue Workflow

## Target Detection

- `https://.../<group>/<project>/-/issues/<id>` means an existing issue target.
- `https://.../<group>/<project>` without `/-/issues/<id>` means create a new issue in that repository.
- No URL or an ambiguous URL means ask the user for the target repo or issue URL before submission.

## Confirmation Checklist

Before submission, confirm:

- Target GitLab repo or issue URL.
- Whether the action is create new issue, update existing issue, or comment on existing issue.
- Issue title.
- Final body with `任务`, `背景描述`, `依赖`, `预期效果`, `评测`.

## Submission Priority

1. Use an available GitLab MCP/API only when configured, authenticated, and the user has confirmed the target/action.
2. Use browser/manual workflow only when the user asks for it or API tools are unavailable but browser access is appropriate.
3. Otherwise output a draft and exact next action. Do not claim submission succeeded without an observed GitLab result.

## GitLab API Notes

- Before using a configured `GITLAB_URL`, verify it is the API root by calling `/api/v4/projects/<urlencoded-project>` and checking that the response is JSON. Some local env files may store a GitLab URL plus project-path lists; do not append `/api/v4` to that value blindly.
- For `gitlab.chehejia.com`, prefer the explicit API root `https://gitlab.chehejia.com` when the configured URL is not a plain host root.
- Git HTTPS credentials from `git credential fill` may authenticate clone/fetch but still fail GitLab REST API calls with `401`; treat that as a non-API credential and look for a real GitLab token from the approved local env source instead.
- In this environment, the approved fallback token source can be `~/.claude/feishu.env`; load it only at execution time and never print token values.
- Load GitLab tokens only at execution time, do not print token values, and report only status code, content type, issue IID, and web URL.

## Existing Issue Handling

For an existing issue URL, prefer commenting with the generated structured content unless the user explicitly asks to overwrite the issue description. Do not close, reopen, assign, delete, or relabel issues without explicit instruction.

Do not reuse an existing issue or MR from previous conversation context, branch history, or local notes. If the current user request does not explicitly provide an issue/MR URL or IID, create a new issue/MR for the new submission.

## Fallback Output

When submission is blocked, return:

- Target status: `repo_url`, `issue_url`, or `missing`.
- Missing inputs or permissions.
- Markdown issue draft.
- Suggested next action, such as providing the GitLab repo URL or pasting the draft into the issue.
