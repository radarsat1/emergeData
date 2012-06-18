
/*
 * Functions for real-time accelerometer analysis;
 * Stephen Sinclair 2012, sinclair@music.mcgill.ca
 * http://idmil.org
 */

load('hanning1024.js');
load('trans.js');

/* Create array storage of a desired length. */
function array(n)
{
    var x;
    /* Note: Float32Array seems to be slower than Array, so don't use
     *       it for now.

    if (typeof Float32Array === 'undefined')
        x = new Array(n);
    else {
        x = new Float32Array(n);
        x.slice = x.subarray;
    }

    */
    x = new Array(n);
    return x;
}

/* Delay line: Accept data sample-by-sample and allow access to
 * previous samples. */
function delayline(len)
{
    var d = array(len), i=0;
    for (i=0; i<d.length; i++)
        d[i] = 0;

    var p = 0;

    this.put = function (x) {
        d[p] = x;
        p = (p + 1) % len;
    }

    this.get = function (i) {
        return d[(p+len+i-1)%len];
    }
}

/* Generate a single-sample filter function from a provided IIR
 * kernel. */
function genfilter(B,A)
{
    var x = new delayline(3), y = new delayline(3);
    var i;

    return function(x0)
    {
        var sum = 0;
        x.put(x0);
        for (i=0; i < B.length; i++)
            sum += x.get(-i)*B[i];
        for (i=1; i < A.length; i++)
            sum -= y.get(-i+1)*A[i];
        y.put(sum);
        return sum;
    }
}

/* Generate a pre-computed 2nd-order Butterworth high-pass filter. */
function genHPF()
{
    // High-pass filter
    var B = [ 0.97803048, -1.95606096,  0.97803048];
    var A = [ 1.        , -1.95557824,  0.95654368];
    return genfilter(B,A);
}

function testHPF()
{
    var i, f = genHPF();
    var input = [1,5,-2,3,7,9,-4,3,2];
    var output = [0,0,0,0,0,0,0,0,0];
    for (i=0; i<input.length; i++) {
        output[i] = f(input[i]);
    }
    print(output);
}

/* Given a desired sample rate and window size, produce a function
 * which accepts unevenly-sampled data and windows it, delivering
 * linearly resampled data points to a provided callback. */
function resampleWindow(seconds, rate, hop, func)
{
    var len = rate * seconds;
    var buffer = [];
    return function(timestamp, data) {
        buffer.push({timestamp:timestamp, data:data});
        if ((timestamp - buffer[0].timestamp) >= seconds) {
            /* linear interpolation */
            var T = 1.0/rate;
            var j = 1;
            var prev = buffer[0].timestamp;
            var next = buffer[1].timestamp;
            var hoptime = prev + hop;
            var hopj = 0;

            var window = [];
            for (var i=0; i < data.length; i++)
                window.push(array(len));

            for (var i=0; i < len && j < buffer.length; i++) {
                var time = buffer[0].timestamp + T*i;

                while ((time < prev || time >= next)
                       && j < (buffer.length-1))
                {
                    j++;
                    prev = next;
                    next = buffer[j].timestamp;

                    if (hoptime >= prev && hoptime < next)
                        hopj = j;
                }

                var ratio = (time - prev) / (next-prev);
                for (var k=0; k < data.length; k++)
                    window[k][i] = (  buffer[j-1].data[k] * (1-ratio)
                                    + buffer[j].data[k] * ratio );
            }

            /* callback */
            func(buffer[0].timestamp, window);

            buffer = buffer.slice(hopj);
        }
    }
}

function testResampleWindow()
{
    var w = resampleWindow(1, 10,
                           function(win) { print(win); })
    w(0.1, [2]);
    w(0.3, [5]);
    w(0.4, [1]);
    w(0.5, [9]);
    w(0.7, [3]);
    w(0.9, [6]);
    w(1.1, [4]);
}

function abs(x)
{
    var i, y = array(x.length);
    for (i=0; i < x.length; i++)
        y[i] = (x[i]<0) ? -x[i] : x[i];
    return y;
}

function sum()
{
    var L = arguments[0].length;
    var i, j, y = array(L);
    for (i=0; i < L; i++) {
        y[i] = 0;
        for (j=0; j < arguments.length; j++)
            y[i] += arguments[j][i];
    }
    return y;
}

function scale(x, m)
{
    var i, y = array(x.length);
    for (i = 0; i < x.length; i++)
        y[i] = x[i] * m;
    return y;
}

function max(x)
{
    var i, m = null;
    for (i = 0; i < x.length; i++)
        if (x[i] > m)
            m = x[i];
    return m;
}

function mult(x1, x2)
{
    var i, y = array(x1.length);
    for (i = 0; i < x1.length; i++)
        y[i] = x1[i] * x2[i];
    return y;
}

function correlate(x1, x2)
{
    var sum, a, b;
    var i,j,o;
    var cor = array(x1.length + x2.length - 1);

    for (i=0; i < x1.length + x2.length - 1; i++) {
        sum = 0;
        for (j=0; j < x2.length; j++) {
            if ((i-j) < x1.length && (i-j) >= 0)
                a = x1[i-j];
            else
                a = 0;
            o = x1.length-1-j;
            if (o < x1.length && o >= 0)
                b = x2[o];
            else
                b = 0;
            sum += a*b;
        }
        cor[i] = sum;
    }
    return cor;
}

// Matrix dot product
function dot(a, b)
{
    var i,j,sum;
    var c = new Array(a.length);
    for (i=0; i < a.length; i++)
        c[i] = new Array(b[0].length);

    for (i=0; i < a.length; i++) {
        for (j=0; j < b[0].length; j++) {
            sum = 0;
            for (k=0; k < a[0].length; k++)
                sum += a[i][k] * b[k][j];
            c[i][j] = sum;
        }
    }
    return c;
}

/* Compute the axis-correlation feature: An absolute sum of the
 * correlations between each pair of accelerometer axes. */
function getCor(data)
{
    var w1 = mult(hanning1024, data[0]);
    var w2 = mult(hanning1024, data[1]);
    var w3 = mult(hanning1024, data[2]);
    var cor1 = correlate(w1, w2);
    var cor2 = correlate(w1, w3);
    var cor3 = correlate(w2, w3);

    var cor = sum(abs(cor1), abs(cor2), abs(cor3));
    cor = scale(cor, 1.0/max(cor));
    return cor;
}

/* Return the first two principle components of an axis-correlation
 * feature vector based on a pre-computed transformation matrix.
 * (Really this is just a generic matrix multiplication that happens
 * to be based on data from the off-line PCA analysis. */
function pcaTransform(cor)
{
    var i, corT = new Array(cor.length);
    for (i=0; i < cor.length; i++)
        corT[i] = [cor[i]];

    var pcs = dot(trans, corT);

    var pcsT = new Array(pcs.length);
    for (i=0; i < pcs.length; i++)
        pcsT[i] = pcs[i][0];

    return pcsT;
}

/* Generate a function that accepts accelerometer data at uneven
 * intervals and produces the first two principle components of the
 * axis-correlation feature. */
function analyseAccelerometers(func)
{
    hpf = [genHPF(), genHPF(), genHPF()];
    return resampleWindow(10.24, 100, 2.56,
        function(timestamp, window) {
            var len = window[0].length;
            for (var axis = 0; axis < 3; axis++) {
                for (var i = 0; i < len; i++) {
                    window[axis][i] = hpf[axis](window[axis][i]);
                }
            }
            var cor = getCor(window);
            var pcs = pcaTransform(cor);
            func(timestamp, pcs);
        });
}

function testAnalysis()
{
    var a = analyseAccelerometers(function(timestamp, pcs){
        print([timestamp,pcs]);
    });

    /* Example data */
    load('data.js');
    var T = 1.0/100;
    var k = 0;

    for (var g=0; g<5; g++) {
        var d = data[0][g];
        for (var i = 0; i < d[0].length; i++) {
            a(T*k, [d[0][i], d[1][i], d[2][i]]);
            k ++;
        }
    }
}
