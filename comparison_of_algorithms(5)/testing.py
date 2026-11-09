import os
import pandas as pd
from scipy import stats

ALPHA = 0.05

# looping 1-5 problem files
for i in range(1, 6):
  path = 'data/problem{}.csv'.format(i)
  if not os.path.exists(path):
    print(' {} not found, skipping'.format(path))
    continue

  df = pd.read_csv(path)
  a = df['Algorithm A'].dropna()
  b = df['Algorithm B'].dropna()
  print(path)

  # Step 1: Welsh's test needs n >= 30 meaning TEST 1 == TRUE, drop if doesnt CLT hold
  print('STEP 1: n_A = {}, n_B = {} -> CLT applies: {}'.format(
    len(a), len(b), len(a) >= 30 and len(b) >= 30))
  if len(a) < 30 or len(b) < 30:
    print(' CLT does not apply -> Welch t-test not valid, stop')
    continue

  # Step 2: Lower is better
  print('STEP 2: H0: mean(A) >= mean(B)   H1: mean(A) < mean(B)')

  # Step 3: comoparing means
  mean_a, mean_b = a.mean(), b.mean()
  print('STEP 3: mean(A) = {:.3f}, mean(B) = {:.3f}'.format(mean_a, mean_b))
  if mean_a >= mean_b:
    print(' A is not better than B on average -> no evidence, stop')
    continue

  # Step 4: Welsh's t-test *(T.TEST([DATA1],[DATA2],1,3)*
  t, p = stats.ttest_ind(a, b, equal_var=False, alternative='less')
  print('STEP 4: p = {:.6f}'.format(p))
  if p < ALPHA:
    print('        p < {} -> reject H0: evidence A is better than B'.format(ALPHA))
  else:
    print('        p >= {} -> cannot reject H0: no evidence A is better'.format(ALPHA))