# MarkGraph 시각화 예시

## 1. 기본 그래프 조회

### 요청
```
get_structure(paths=["/Users/me/notes"])
```

### 응답 예시
```json
{
  "nodes": [
    { "id": "DailyNote", "type": "file", "label": "Daily Note", "metadata": {} },
    { "id": "ProjectA", "type": "file", "label": "Project A", "metadata": { "status": "active" } },
    { "id": "ProjectB", "type": "file", "label": "Project B", "metadata": {} },
    { "id": "#project", "type": "tag", "label": "project", "metadata": {} },
    { "id": "#important", "type": "tag", "label": "important", "metadata": {} }
  ],
  "links": [
    { "source": "DailyNote", "target": "ProjectA", "relation": "wikilink", "metadata": {} },
    { "source": "DailyNote", "target": "ProjectB", "relation": "wikilink", "metadata": {} },
    { "source": "ProjectA", "target": "#project", "relation": "tag", "metadata": {} },
    { "source": "ProjectA", "target": "#important", "relation": "tag", "metadata": {} },
    { "source": "ProjectB", "target": "#project", "relation": "tag", "metadata": {} }
  ]
}
```

## 2. 이웃 노드 조회

### 요청
```
get_structure_and_query(
    paths=["/Users/me/notes"],
    node_id="ProjectA",
    depth=1
)
```

### 응답 예시
ProjectA와 직접 연결된 노드만 포함된 서브그래프:

```json
{
  "nodes": [
    { "id": "ProjectA", "type": "file", "label": "Project A", "metadata": { "status": "active" } },
    { "id": "DailyNote", "type": "file", "label": "Daily Note", "metadata": {} },
    { "id": "#project", "type": "tag", "label": "project", "metadata": {} },
    { "id": "#important", "type": "tag", "label": "important", "metadata": {} }
  ],
  "links": [
    { "source": "DailyNote", "target": "ProjectA", "relation": "wikilink", "metadata": {} },
    { "source": "ProjectA", "target": "#project", "relation": "tag", "metadata": {} },
    { "source": "ProjectA", "target": "#important", "relation": "tag", "metadata": {} }
  ]
}
```

## 3. 시각화 생성

### CLI 사용
```bash
# 그래프 데이터를 JSON 파일로 저장 후
python visualize.py graph.json output.html
```

### Python 직접 사용
```python
import json
from pathlib import Path

# MCP 응답 데이터
graph_data = {
    "nodes": [...],
    "links": [...]
}

# visualize.py 로드
exec(Path(".claude/skills/markgraph-skill/scripts/visualize.py").read_text())

# HTML 생성
html = generate_html(graph_data)
Path("my_graph.html").write_text(html)
```

## 4. 시각화 결과

생성된 HTML 파일을 브라우저에서 열면:

- **노드**: 파일(청록색), 태그(빨간색)로 구분
- **링크**: wikilink(실선), embed(점선), tag(작은 점선)으로 구분
- **인터랙션**:
  - 노드 드래그로 위치 조정
  - 마우스 휠로 줌 인/아웃
  - 노드 호버 시 정보 툴팁

## 5. 복잡한 그래프 예시

중첩 태그와 임베드가 포함된 예시:

```json
{
  "nodes": [
    { "id": "MOC", "type": "file", "label": "Map of Content", "metadata": {} },
    { "id": "Note1", "type": "file", "label": "Note 1", "metadata": {} },
    { "id": "Note2", "type": "file", "label": "Note 2", "metadata": {} },
    { "id": "Image", "type": "file", "label": "Image", "metadata": {} },
    { "id": "#project/frontend", "type": "tag", "label": "project/frontend", "metadata": {} },
    { "id": "#status/wip", "type": "tag", "label": "status/wip", "metadata": {} }
  ],
  "links": [
    { "source": "MOC", "target": "Note1", "relation": "wikilink", "metadata": {} },
    { "source": "MOC", "target": "Note2", "relation": "wikilink", "metadata": {} },
    { "source": "Note1", "target": "Image", "relation": "embed", "metadata": {} },
    { "source": "Note1", "target": "#project/frontend", "relation": "tag", "metadata": {} },
    { "source": "Note2", "target": "#project/frontend", "relation": "tag", "metadata": {} },
    { "source": "Note2", "target": "#status/wip", "relation": "tag", "metadata": {} }
  ]
}
```

이 그래프는 MOC(Map of Content) 패턴과 중첩 태그 사용을 보여줍니다.
