# PixG — 파라미터

모든 값은 `workflows/` 의 ComfyUI 워크플로우 JSON과 `src/postprocessing.py` 에서 직접 읽어낸 실측값입니다.

## 1. 캐릭터 스프라이트 생성 (AnimateDiff Vid2Vid)

| 항목 | 값 |
|---|---|
| 모션 모듈 | `animatediffMotion_v15V2.ckpt` (초기 `mm_sd_v14.ckpt`) |
| beta schedule | `sqrt_linear (AnimateDiff)` |
| **context_length** | **16** (11-27판은 12) |
| context stride / overlap | 1 / 0~1 |
| context schedule | `uniform` |
| 체크포인트 | `cardosAnime_v20` · `dragonfruitUnisex_v10` · `aingdiffusion_v12` (전부 SD 1.5) |
| steps / cfg | **20 / 8** |
| 샘플러 / 스케줄러 | `dpmpp_2m_sde_gpu` / `karras` |
| 해상도 | 512 × 512 |
| CLIP skip | -2 |
| 출력 | GIF 16 fps (초기 8 fps) |

샘플러는 `euler/normal`(초기) → `dpmpp_sde/karras` → `dpmpp_2m_sde_gpu/karras`(최종) 순으로 바뀌었습니다. `workflows/ui/` 를 번호순으로 열면 튜닝 과정이 그대로 보입니다.

### ControlNet — 가중치를 일부러 다르게 줬습니다

| ControlNet | strength | 왜 |
|---|---|---|
| **OpenPose** | **1.0** | 포즈가 곧 "동작"이므로 꽉 고정 |
| **Depth** | **0.2** | 형태 보조용. 높이면 음영이 과해져 픽셀 아트의 단순한 면이 깨짐 |

전처리기: `OpenposePreprocessor` · `DWPreprocessor` · `Zoe-DepthMapPreprocessor`
Canny는 실험만 하고 최종 파이프라인에는 넣지 않았습니다.

### LoRA

| LoRA | weight | 용도 |
|---|---|---|
| `CspPixelArt_Style-20` | 0.5 ~ 1.0 | 픽셀 아트 스타일 (최종 채택) |
| `vscharacter64-v1` | 1.0 | 64px 캐릭터 스프라이트 |
| `pixel_4` | 0.5 | 픽셀화 보조 |

픽셀 LoRA는 9종을 받아 비교한 뒤 위 조합을 골랐습니다. 비교만 하고 채택하지 않은 목록은 `models/manifest.json` 의 `_loras_compared_but_not_final` 에 있습니다.

### 프롬프트

포지티브에 공통으로 넣은 것 — `(white background:1.2~1.4)` · `(simple background)` · `(character only)`
배경 제거 후처리를 쉽게 하려고 **생성 단계에서부터 배경을 단순화**했습니다.

네거티브 임베딩 4종 — `easynegative` · `FastNegativeV2` · `NegfeetV2` · `bad-hands-5`
캐릭터 스프라이트에서는 **사지가 깨지는 것이 가장 치명적**이라 손·발 관련 임베딩을 골라 넣었습니다.

## 2. 건물·사물 생성

캐릭터와 **다른 체크포인트를 씁니다.**

| 항목 | 값 |
|---|---|
| 체크포인트 | `handpaintedRPGIcons_v1` / `anyloraCheckpoint` |
| LoRA | `Isometric_Setting` (1.0) |
| steps / cfg | 20 / **10** |
| 샘플러 | `dpmpp_sde` / `karras` |
| 네거티브 | `"character, human, person, people, male, female, man, woman"` — 사람이 나오지 않도록 명시 배제 |
| ControlNet | strength `0` — 사실상 끔 (고정할 포즈가 없음) |

## 3. 후처리 (`src/postprocessing.py`)

| 단계 | 구현 | 출력 |
|---|---|---|
| 1. 최신 GIF 탐색 | `glob('../output/*.gif')[-1]` | — |
| 2. 프레임 추출 | PIL `image.seek()` 루프 | `pre_rm_bg/` |
| 3. 배경 제거 | `transparent_background.Remover` (InSPyReNet) — `rgba`판 + 흰 배경판 **동시 생성** | `rm_bg_png/` · `rm_bg_white/` |
| 4. GIF 재조립 | `imageio.mimwrite` · duration 0.05 · loop 0 | `rm_bg_gif/` |
| 5. 격자 배치 | `cv2.resize(64,64)` → 8개씩 `hstack` → `vstack` | `spritesheet/` |

### 격자 규칙

```python
y = cv2.resize(y,(64,64))          # 전 프레임 64×64 강제 통일
... 8개씩 hstack → 줄 단위로 vstack   # 가로 8칸 격자
# 8의 배수가 아니면 np.zeros((64,64,4)) 투명 프레임으로 패딩
```

프레임 수에 따라 분기 3개(`%8==0` / `>8` / `<8`)를 두어 **어떤 프레임 수가 들어와도 격자가 깨지지 않게** 했습니다.

### 배경 제거를 두 벌 만드는 이유

- `rgba` (투명) → 스프라이트 시트용
- `[255,255,255]` (흰 배경) → GIF 미리보기용

GIF는 투명도를 제대로 담지 못해 미리보기가 깨지기 때문입니다.

## 4. 화질 복원 모델

| 모델 | scale | 역할 |
|---|---|---|
| `1x-DeJpeg-Fatality-PlusULTRA.pth` | **1x** | JPEG 아티팩트 제거 |
| `1x_PixelSharpen_100000.pth` | **1x** | 픽셀 경계 샤프닝 |

둘 다 **1x** 입니다 — 해상도를 올리지 않고 화질만 복원합니다. 실제 흐름은 `1x 복원 → 64×64 축소` 로, **축소하기 전에 경계를 살려두는 것**이 목적이었습니다.

## 측정하지 않은 것

일관성 개선의 **정량 비교 지표는 남기지 않았습니다.** 당시엔 "ZEP에 올려서 아바타로 동작하는가"를 합격 기준으로 삼았습니다. 이 점은 이후 프로젝트에서 정확도·응답시간을 수치로 관리하는 방식으로 고쳤습니다.
