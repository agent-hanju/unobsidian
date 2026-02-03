# MarkGraph

Obsidian 스타일 마크다운 파일을 파싱하여 지식 그래프로 변환하는 MCP 서버.

## 특징

- **경량**: 최소 의존성 (mcp, pydantic, python-frontmatter)
- **D3.js 호환**: 출력 JSON을 d3.forceSimulation()에서 바로 사용 가능
- **이웃 조회**: BFS 기반 이웃 탐색, depth 설정 가능
- **Obsidian 문법 지원**: wikilinks, tags, embeds, frontmatter

## 설치

```bash
pip install markgraph
# 또는
uv add markgraph
```

## 사용법

### Claude Desktop

`~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "markgraph": {
      "command": "uvx",
      "args": ["markgraph"]
    }
  }
}
```

### Claude Code CLI

```bash
claude mcp add markgraph -- uvx markgraph
```

### MCP 도구

#### `get_structure`

마크다운 파일을 파싱하여 전체 그래프 반환.

```json
{
  "paths": ["/path/to/vault"]
}
```

**응답:**
```json
{
  "nodes": [
    { "id": "NoteA", "type": "file", "label": "Note A", "metadata": {} }
  ],
  "links": [
    { "source": "NoteA", "target": "NoteB", "relation": "wikilink" }
  ]
}
```

#### `query_neighbors`

마크다운 파일을 파싱하여 특정 노드의 이웃을 조회.

```json
{
  "paths": ["/path/to/vault"],
  "node_id": "MyNote",
  "depth": 2
}
```

## 데이터 모델

### Node

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 파일명 또는 #태그명 |
| `type` | "file" \| "tag" | 노드 타입 |
| `label` | string? | 표시용 레이블 |
| `metadata` | object | frontmatter 데이터 |

### Link

| 필드 | 타입 | 설명 |
|------|------|------|
| `source` | string | 출발 노드 ID |
| `target` | string | 도착 노드 ID |
| `relation` | "wikilink" \| "embed" \| "tag" | 관계 타입 |
| `metadata` | object | 추가 메타데이터 |

## 파싱 규칙

| 패턴 | relation |
|------|----------|
| `[[Target]]` | wikilink |
| `[[Target\|Alias]]` | wikilink |
| `![[Embed]]` | embed |
| `#Tag` | tag |

**파싱 제외 영역:**
- 코드 펜스 (` ``` `)
- 인라인 코드 (`` ` ``)
- YAML frontmatter (별도 추출)

## 시각화

`.claude/skills/markgraph-skill/scripts/visualize.py` 스크립트로 D3.js 기반 HTML 생성:

```bash
python visualize.py graph.json output.html
```

## 개발

```bash
# 의존성 설치
uv sync

# 테스트 실행
pytest tests/

# MCP Inspector로 테스트
npx @anthropic-ai/mcp-inspector markgraph
```

## 라이선스

MIT
