
# RMS and periodicity
# -------------------

rms_periodicity = {
    'still': 1.0,
    'fistpump': 0.389581922515,
    'jumping': 0.721581938743,
    'standing': 1.0,
    'overhead': 0.420024667843,
    'fastwaving': 1.0,
    'bouncing': 1.0,
    'swaying': 0.770067018747,
    'stepping': 1.0,
    'fast': 0.622911741529,
    'slow': 0.804708577246,
    'wave': 1.0
    }

# RMS only
# --------

rms_only = {
    'still': 1.0,
    'fistpump': 0.44491570731,
    'jumping': 0.741474581623,
    'standing': 1.0,
    'overhead': 0.427862172331,
    'fastwaving': 1.0,
    'bouncing': 1.0,
    'swaying': 0.918218598474,
    'stepping': 1.0,
    'fast': 0.580870764381,
    'slow': 0.953525069992,
    'wave': 1.0
    }

# Periodicity only
# ----------------

periodicity_only = {
    'still': 1.0,
    'fistpump': 0.995117083081,
    'jumping': 1.0,
    'standing': 1.0,
    'overhead': 0.908822656945,
    'fastwaving': 1.0,
    'bouncing': 1.0,
    'swaying': 1.0,
    'stepping': 1.0,
    'fast': 0.992159180457,
    'slow': 1.0,
    'wave': 1.0
    }

# Frequency only
# --------------

frequency_only = {
    'still': 1.000000,
    'fistpump': 0.852212,
    'jumping': 1.000000,
    'standing': 1.000000,
    'overhead': 0.854928,
    'fastwaving': 1.000000,
    'bouncing': 1.000000,
    'swaying': 1.011921,
    'stepping': 1.000000,
    'fast': 0.931738,
    'slow': 1.000000,
    'wave': 1.000000
    }

predictors = [
    rms_periodicity,
    rms_only,
    periodicity_only,
    frequency_only
    ]

tags = sort(list(set().union(*map(set, [p.keys() for p in predictors]))))

xlocations = arange(len(tags),dtype=float)
w = 1.0/(len(predictors)+1)

clf()
colors = 'blue','red','green','orange'
for n, p in enumerate(predictors):
    bar(xlocations-len(predictors)/2*w+n*w,
        [p.get(t) for t in tags],
        width=w, color=colors[n], label=['rms_periodicity',
    'rms_only',
    'periodicity_only',
    'frequency_only'][n]
)
xlim(-1,len(tags))
ylim(0,1.5)
xticks(xlocations, tags)
legend()
title('prediction results for video tags, workshop 1.5')
