from scipy import stats

def thompson_sample(prior_betas, word):
    X = stats.beta(prior_betas[word]["alpha"], prior_betas[word]["beta"])
    return X.rvs()

def update_beta_distributions(prior_betas, valid_words_dict):
    for word in prior_betas.keys():
        if word not in valid_words_dict:
            prior_betas[word]["beta"] += 1
        else: 
            prior_betas[word]["alpha"] += 1
    
    return prior_betas
