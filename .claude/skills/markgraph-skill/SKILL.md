# MarkGraph Skill

마크다운 지식 그래프를 조회하고 시각화하는 방법을 안내합니다.

## MCP 도구

MarkGraph MCP 서버가 제공하는 도구:

### `get_structure`
마크다운 파일들을 파싱하여 지식 그래프를 반환합니다.

```
입력: paths (list[str]) - 파일 또는 디렉토리 경로 배열
출력: {"nodes": [...], "links": [...]}
```

**예시:**
```json
{
  "paths": ["/path/to/vault"]
}
```

### `query_neighbors`
특정 노드의 이웃 노드들을 조회합니다.

```
입력:
  - node_id (str) - 노드 ID (파일명 또는 #태그명)
  - depth (int, 기본값=1) - 탐색 깊이 (1-3)
출력: 서브그래프 JSON
```

### `get_structure_and_query`
그래프 구축과 이웃 조회를 한 번에 수행합니다.

```
입력:
  - paths (list[str]) - 경로 배열
  - node_id (str) - 노드 ID
  - depth (int, 기본값=1) - 탐색 깊이
출력: 서브그래프 JSON
```

## 데이터 구조

### Node
```json
{
  "id": "MyNote",
  "type": "file",
  "label": "My Note",
  "metadata": {"author": "John"}
}
```

- `type`: `"file"` 또는 `"tag"`
- 태그 노드의 id는 `#`로 시작 (예: `#project`)

### Link
```json
{
  "source": "NoteA",
  "target": "NoteB",
  "relation": "wikilink",
  "metadata": {}
}
```

- `relation`: `"wikilink"`, `"embed"`, `"tag"` 중 하나

## 시각화

그래프를 시각화하려면 `scripts/visualize.py` 스크립트를 사용합니다.

### 사용법

1. MCP 도구로 그래프 데이터 조회
2. JSON 데이터를 파일로 저장
3. visualize.py 실행하여 HTML 생성

```bash
python scripts/visualize.py graph.json output.html
```

또는 Python에서 직접 호출:

```python
from pathlib import Path
import json

# 그래프 데이터 (MCP 응답)
graph_data = {
    "nodes": [...],
    "links": [...]
}

# visualize.py의 generate_html 함수 사용
exec(Path("scripts/visualize.py").read_text())
html = generate_html(graph_data)
Path("graph.html").write_text(html)
```

## 예시 워크플로우

### 전체 그래프 시각화
1. `get_structure(paths=["/my/vault"])` 호출
2. 결과를 `graph.json`으로 저장
3. `python visualize.py graph.json graph.html` 실행
4. 브라우저에서 `graph.html` 열기

### 특정 노트 주변 탐색
1. `get_structure_and_query(paths=["/my/vault"], node_id="ProjectA", depth=2)` 호출
2. 결과로 서브그래프 시각화

## 참고

- 시각화 예시: [reference/EXAMPLES.md](reference/EXAMPLES.md)
- D3.js forceSimulation 기반 인터랙티브 그래프
- 노드 드래그, 줌/팬 지원
