import scipy as sc
import numpy as np
import pandas as pd
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import sys
#np.set_printoptions(threshold=sys.maxsize) # This allows to you to print large arrays without truncating them

#=================================================================================================#

# PARAMETERS 

runs   = 10            # How many times we run the simulation
J      = 5               # Number of food sources (aka, number of trails to food sources)
N      = 5000            # Total number of ants
alpha  = 9.170414e+01    # Per capita rate of spontaneous discoveries
s      = 8.124702e+01    # Per capita rate of ant leaving trail per distance
gamma1 = 1.186721e+01    # Range of foraging scouts
gamma2 = 5.814424e-06    # Range of recruitment activity 
gamma3 = 1.918047e-03    # Range of influence of pheromone 
K      = 8.126483e-03    # Inertial effects that may affect pheromones 
n1     = 1.202239e+00    # Individual ant's contribution to rate of recruitment (orig. eta1)
n2     = 9.902102e-01    # Pheromone strength of trail (originally eta2)

Qmin = 0                 # Minimum & Maximum of Quality uniform distribution
Qmax = 20
Dmin = 0                 # Minimum & Maximum of Distance uniform distribution
Dmax = 0.5

betaB  = np.zeros(J)     # How much each ant contributes to recruitment to a trail
betaS  = np.zeros(J)     # Relationship btwn pheromone strength of a trail & its quality

# TIME 

start = 0.0
stop  = 50.0
step  = 0.005
tspan = np.arange(start,stop+step,step)

# INITIAL CONDITIONS

x0 = np.zeros(J)         # We start with no ants on any of the trails

#=================================================================================================#

# SYSTEM OF EQUATIONS

def dx_dt(x,t,Q,D,betaB,betaS):
    """
    Creates a list of J equations describing the number of ants
    on each of the J trails. (Eqn i corresponds to food source i)
    """
    system = np.zeros(J)
    system = (alpha* np.exp(-gamma1*D) + (gamma2/D)*betaB*x)*(N-sum(x)) - (s*D*x)/(K+ (gamma3/D)*betaS*x)
    return system

# RUNS AND MODEL OUTPUT

density      = np.zeros([runs,J])
final_time   = np.zeros([runs,J])
weight_avg_Q = np.zeros(runs)
weight_avg_D = np.zeros(runs)
prop_committed_ants    = np.zeros(len(tspan))   # Proportion of committed ants 
prop_noncommitted_ants = np.zeros(len(tspan))   # Proportion of non committed ants 

def simulation():
    for w in range(runs):
        Q = np.random.uniform(Qmin,Qmax,J)      # Choose each trail's quality from uniform distrib      
        D = np.random.uniform(Dmin,Dmax,J)    # Choose each trail's distance from uniform distrib     
        betaB = n1 * Q
        betaS = n2 * Q

        xs = odeint(dx_dt, x0, tspan, args=(Q,D,betaB,betaS))           # Solve the system, Columns: trail (food source), Rows: time step
        final_time[w,:] = xs[-1,:]              # 2D array of the number of ants on each trail at the last timestep. Columns: trail (food source), Rows: runs.
    
        weight_avg_Q[w]  = sum((final_time[w,:] * Q)/N)  # Weighted average of quality (selected.Q in R)
        weight_avg_D[w]  = sum((final_time[w,:] * D)/N)  # Weighted average of distance (selected.D in R)


param            = np.linspace(9,15,3)
param_values     = []
weight_avg_Q_tot = []
weight_avg_D_tot = []
for p in range(len(param)):
    gamma1 = param[p]
    param_values += ([param[p]] * runs)
    simulation()
    weight_avg_Q_tot += list(weight_avg_Q)
    weight_avg_D_tot += list(weight_avg_D)

#=================================================================================================#

# PROCESSING DATA

Q_bins = np.arange(Qmin,Qmax+0.5,0.5)
Q_hist,Q_edges = np.histogram(weight_avg_Q, bins = Q_bins)
#print('Q_hist: ',Q_hist)
#print('Q_edges: ',Q_edges)

Q_distr = np.zeros(len(Q_bins))
Q_distr = Q_hist/(runs) 

D_bins = np.arange(Dmin,Dmax+0.01,0.01)
D_hist,D_edges = np.histogram(weight_avg_D, bins = D_bins)
#print('D_hist: ',D_hist)
#print('D_edges: ',D_edges)

D_distr = np.zeros(len(D_bins))
D_distr = D_hist/(runs)


#=================================================================================================#

# CREATING CSV

d = {'Param Values': param_values, 'WeightedQ': weight_avg_Q_tot,'WeightedD': weight_avg_D_tot}
df = pd.DataFrame(data=d)
print(df)

#=================================================================================================#

# Plotting

plt.rc('font', family='serif')

# The number of ants on each trail over time
#plt.figure()
#for i in range(J):
#    plt.plot(tspan, xs[:,i], label = str(i+1)) 
#plt.title('Number of ants over time',fontsize=15)
#plt.xlabel('Time',fontsize=15)
#plt.ylabel('Number of ants',fontsize=15)
#plt.legend(title='Trail', bbox_to_anchor=(1.01, 0.5), loc='center left', borderaxespad=0.)

# The proportion of ants committed to a trail
#plt.figure()
#plt.plot(tspan, prop_committed_ants) 
#plt.title('Proportion of committed ants',fontsize=15)
#plt.xlabel('Time',fontsize=15)
#plt.ylabel('Proportion',fontsize=15)

# Plotting histogram of weighted average of quality
#plt.figure()
#plt.bar(Q_edges, Q_hist, width = 0.5, color='#0504aa',alpha=0.7)
#plt.title('Histogram of weighted av Q in trials',fontsize=15)
#plt.xlabel('bins',fontsize=15)
#plt.ylabel('weighted Q',fontsize=15)

# Plotting histogram of weighted average of quality
#plt.figure()
#plt.hist(weight_avg_Q, bins = 50)
#plt.title('Histogram of weighted av Q in trials',fontsize=15)
#plt.xlabel('weighted Q',fontsize=15)
#plt.ylabel('count',fontsize=15)

# Plotting histogram of weighted average of distance
#plt.figure()
#plt.hist(weight_avg_D, bins = 50)
#plt.title('Histogram of weighted av D in trials',fontsize=15)
#plt.xlabel('weighted D',fontsize=15)
#plt.ylabel('count',fontsize=15)

# Plotting Probability distribution of weighted average of quality
plt.figure()
plt.bar(Q_bins[:-1], Q_distr, width = 0.5, color='#0504aa',alpha=0.7)
plt.title('Distribution Weighted average of Quality',fontsize=15)
plt.xlabel('Weighted Average of Quality',fontsize=15)
plt.ylabel('Probability',fontsize=15)

# Plotting Probability distribution of weighted average of distance
plt.figure()
plt.bar(D_bins[:-1], D_distr, width = 0.01, color='#0504aa',alpha=0.7)
plt.title('Distribution Weighted average of Distance',fontsize=15)
plt.xlabel('Weighted Average of Distance',fontsize=15)
plt.ylabel('Probability',fontsize=15)

plt.show()
