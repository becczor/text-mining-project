#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Stian Rødven Eide

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import re
import os
import sys
import codecs
import itertools as it
import bz2


def combination_to_out(combination, savelex):
    '''This function takes a single combination and fills the savelex
    dictionary with its items, making sure each MWE only occurs once.
    If savelex is already filled, combination can be an empty list.
    Returns the lexes as a list.'''
    # The combination might be an empty list, in which case we assume
    # that savelex already have all lexes. We then simply return
    # the values of savelex as a list
    if not combination:
        lexes_out = [savelex[l] for l in savelex]
        return lexes_out
    # Combinations may be tuples, so we make sure they are not
    combination = list(combination)
    lexes_out = []
    # We go through all the word positions in savelex and fill those
    # that are missing
    for i in sorted(savelex):
        if savelex[i] == None:
            # if combination[0] has a colon pointing to a position and
            # that position is filled by the lex referred to, remove
            # the savelex instead of setting it to combination[0]. This
            # is how we contract the MWE
            if ':' in combination[0]:
                # We set ref_post to the number after the colon. If the colon
                # signifies something else, we save and continue
                try:
                    ref_post = re.match('(.+:)(\d+)', combination[0]).group(2)
                except AttributeError:
                    savelex[i] = combination[0]
                    combination.pop(0)
                    continue
                # We see whether it matches whatever it refers to
                if (int(ref_post)-1) in savelex:
                    if (re.sub(':\d+','',combination[0]) ==
                        re.sub(':\d+','',savelex[int(ref_post)-1])):
                        # And if so, delete that item
                        savelex.pop(i)
                        combination.pop(0)
                        continue
            # Otherwise, we save the current lex in the combination
            savelex[i] = combination[0]
            combination.pop(0)
        lexes_out.append(savelex[i])
    return lexes_out


def get_valid_combinations(combinations, savelex):
    '''A helper function to remove combinations of lexes that we know
    are referentially invalid. This can either be that a lex C refers
    to a lex B that refers to a lex A, or that a lex refers to another
    lex that doesn't exist.'''
    # We need to update this now, since we have joined the strings of
    # various options
    valid_combinations = [c for c in combinations]
    for c in combinations:
        removed = False
        mwes = [l for l in c if sep in l and
                not (l.startswith(sep) or l.startswith('http'))]
        # If there are no MWEs, the combination is probably valid
        if not mwes:
            continue
        # If a MWE-lex only matches itself, we discard the combination
        for l in mwes:
            matches = [l2 for l2 in mwes
                       if re.sub('\.\..+','',l2) == re.sub('\.\..+','',l)]
            if len(matches) == 1:
                valid_combinations.remove(c)
                removed = True
                break
        if removed == True:
            continue
        # We make a copy of c and savelex so that we can manipulate them
        tmpc = [l for l in c]
        tmpsavelex = {k:savelex[k] for k in savelex}
        # We populate the temporary savelex, replacing all instances of
        # None with the lexes from the current combination
        for i in sorted(tmpsavelex):
            if tmpsavelex[i] == None:
                tmpsavelex[i] = tmpc[0]
                tmpc.pop(0)
        # We go through the fully populated temporary savelex, checking
        # that all references are valid
        for i in sorted(tmpsavelex):
            # If the current MWE lex has a referencing number
            if (sep in tmpsavelex[i] and ':' in tmpsavelex[i]
                and not tmpsavelex[i].startswith(sep)):
                # we get the lex base and its ref number
                clist = tmpsavelex[i].split(':')
                ref = clist[-1]
                lbase = ':'.join(clist[:-1])
                lbase = lbase.split('..')[0]
                try:
                    ref = int(ref)
                except ValueError:
                    break
                try:
                    reflex = tmpsavelex[ref-1]
                except KeyError:
                    valid_combinations.remove(c)
                    break
                refbase = reflex.split('..')[0]
                # If whatever the lex refers to has a colon we know
                # that it is invalid and remove the combination
                if ':' in reflex:
                    valid_combinations.remove(c)
                    break
                # If the base of the lex differs from the lex it
                # refers to, it is also invalid
                elif not lbase == refbase:
                    valid_combinations.remove(c)
                    break
    return valid_combinations


def comp_lex(lex):
    '''Compresses a lex or saldo value, removes POS and conj/sense
    number. Returns the base, plus potential ref numbers. This
    is in order to compare two lex/saldo values to see if they are
    similar enough to be joined.
    '''
    # If it ends with a colon, followed by digits
    if re.match('.+:\d+$',lex):
        # we set fbase to everything before the colon
        # and fref to the digits after the colon
        flist = lex.split(':')
        fbase = ':'.join(flist[:-1])
        fref = flist[-1:][0]
        # We are reasonably sure that fbase now ends with . followed
        # by one or more digits. Actually, POS may be different too, and
        # that should also be OK. Which means we should set the base
        # to just before the double fullstops
        flem = lex.split('..')[0]
        fcomp = flem + fref
    # If it has no reference number
    else:
        fcomp = lex.split('..')[0]
    return fcomp


def join_identicals(lexes):
    '''A helper function to join lexes we are unable to choose one of.
    Works only for saldo/lex modes
    In the case that there are items in the input list that have identical
    bases, i.e. the only difference is the SALDO POS or number, we remove all
    but the first one.'''
    # Trying from scratch
    newlexes = []
    while lexes:
        # fl = first_of_list, rl = rest_of_list
        fl, rl = lexes[0], lexes[1:]
        fcomp = comp_lex(fl)
        rcomps = [comp_lex(l) for l in rl]
        if fcomp not in rcomps:
            newlexes.append(fl)
            lexes.pop(0)
            continue
        else:
            tojoin = [fl]
            for l in rl:
                rcomp = comp_lex(l)
                if fcomp == rcomp:
                    tojoin.append(l)
            for l in tojoin:
                lexes.remove(l)
            newlexes.append('|'.join(tojoin))
    return newlexes


def remove_identicals(full_list):
    '''A helper function to remove lexes we know we don't need.
    It should work with a list of lexes for a single word or with a list
    of lists of lexes for a whole sentence.
    In the case that there are items in the input list that have identical
    bases, i.e. the only difference is the SALDO POS or number, we remove all
    but the first one.'''
    # We make reduced_list a copy of the input list
    reduced_list = [c for c in full_list]
    for i, c in enumerate(full_list):
        # If the items in the list are lists or tuples, we join
        # them to a string
        if type(c) == tuple or type(c) == list:
            c = ' '.join(c)
        # We remove everything except the base from the lex(es)
        # ex: slå_fast..vbm.1:11 -> slå_fast
        cstrip = re.sub('\.{2}.+?\d+:?\d*','',c)
        # Unless we are at the final item in the list, we compare the base
        # of the lex(es) to the rest of the list. If the base of an item in the
        # rest of the list is identical to the base of the current item, we
        # remove it.
        if len(full_list) > i:
            for c2 in full_list[i+1:]:
                if type(c2) == tuple or type(c) == list:
                    c2 = ' '.join(c2)
                c2strip = re.sub('\.{2}.+?\d+:?\d*','',c2)
                if c2strip == cstrip:
                    if c2 in reduced_list:
                        reduced_list.remove(c2)
    return reduced_list


def get_max_mwe_words(combinations):
    '''A helper function that finds the maximum number of MWE words
    possible among the combinations and removes all combinations that
    have fewer MWE words than that number. It does so by counting
    underscores, which should correspond to MWEs. It should, however,
    not be used before removing referentially invalid combinations'''
    max_combinations = []
    max_underscores = -1
    for c in combinations:
        underscores = 0
        for l in c:
            if '..' in l and not (l.startswith(sep) or l.startswith('http')):
                lbase = l.split('..')[0]
                underscores += (len(lbase.split(sep))-1)
        if underscores > max_underscores:
            max_underscores = underscores
    for c in combinations:
        underscores = 0
        for l in c:
            if '..' in l and not (l.startswith(sep) or l.startswith('http')):
                lbase = l.split('..')[0]
                underscores += (len(lbase.split(sep))-1)
        if underscores == max_underscores:
            max_combinations.append(c)
    return max_combinations


def remove_leading_non_mwes(combinations, savelex):
    '''A helper function to move all lexes preceeding the first MWE from
    combinations to savelex. The number of lexes to be moved are
    determined by the combination with the leftmost MWE, thereby
    ensuring that all combinations keep the same length.'''
    # In case we already filled savelex and combinations is empty, we
    # simply return the input
    if not combinations:
        return combinations, savelex
    mincounter = None
    # We check how many lexes there are before the first MWE word in the
    # combination with the least lexes before the first MWE word
    for c in combinations:
        counter = 0
        for l in c:
            if sep in l and not l.startswith(sep):
                break
            else:
                counter += 1
        if not mincounter or counter < mincounter:
            mincounter = counter
    # If there are any lexes before the first MWE word, we proceed to
    # save them and remove them from all combinations
    if mincounter > 0:
        reduced_combinations = []
        remwords = []
        # We use the lexes from the first combination
        for i in range(mincounter):
            remwords.append(combinations[0][i])
        # Then we remove them from all combinations
        for c in combinations:
            reduced_combinations.append(c[mincounter:])
        combinations = [c for c in reduced_combinations if c]
        # Lastly, we add them to savelex
        savecount = 0
        for l in sorted(savelex):
            if savecount == mincounter:
                break
            if savelex[l] == None:
                savelex[l] = remwords[savecount]
                savecount += 1
    return combinations, savelex


def get_best_leftmost(combinations):
    '''A helper function that removes all combinations where the first
    MWE is shorter than in other combinations.
    '''
    # TODO: We should also make sure that we only count MWE lexes that
    # refer to the first MWE lex. As it is now, we would give preference
    # also to combinations where the first MWE is used multiple times
    reduced_combinations = []
    maxlen = -1
    # First we determine the length of the first MWE in the combination
    # with the longest first MWE
    for c in combinations:
        counter = len([l for l in c if
                       re.sub(':\d+','',l) == re.sub(':\d+','',c[0])])
        if counter > maxlen:
            maxlen = counter
    # Then we remove all combinations where the first MWE is shorter
    # than the longest first MWE
    for c in combinations:
        counter = len([l for l in c if
                       re.sub(':\d+','',l) == re.sub(':\d+','',c[0])])
        if counter == maxlen:
            reduced_combinations.append(c)
    return reduced_combinations


def get_most_compact(combinations):
    '''A helper function that finds, among all combinations, the
    smallest distance between the first lex, which should be part of a
    MWE, and the last lex that it matches. It is currently unused, as
    it might discard combinations where the first MWE is used multiple
    times in the same sentence.'''
    # TODO: We should also make sure that we only count MWE lexes that
    # refer to the first MWE lex. As it is now, we would give preference
    # also to combinations where the first MWE is used multiple times
    reduced_combinations = []
    pos_of_last = 0
    mindist = None
    # First we determine the smallest possible distance, among all
    # combinations, between the first lex and the last lex that it
    # matches
    for c in combinations:
        mwedist = 0
        for i, l in enumerate(c):
            if re.sub(':\d+','',l) == re.sub(':\d+','',c[0]):
                mwedist = i
        if mindist == None or mwedist < mindist:
            mindist = mwedist
    # Then we remove all combinations where the distance is greater
    # than that.
    for c in combinations:
        mwedist = 0
        for i, l in enumerate(c):
            if re.sub(':\d+','',l) == re.sub(':\d+','',c[0]):
                mwedist = i
        if mwedist == mindist:
            reduced_combinations.append(c)
    return reduced_combinations


def save_first_mwe(combinations, savelex):
    '''A helper function that moves the first MWE from the first
    combination to savelex, and then removes the first MWE from all
    combinations. The function assumes that the first MWE is the same
    for all combinations.'''
    # TODO: There might be cases where the first MWE is not the same for
    # all combinations.
    # In case we already filled savelex and combinations is empty, we
    # simply return the input
    if not combinations:
        return combinations, savelex
    reduced_combinations = []
    # The first lex should be part of a MWE
    first_mwe_lex = combinations[0][0]
    # This list will hold the word positions of all lexes that are part
    # of the first MWE
    mwe_positions = [0]
    # This list will hold the lexes that are part of the first MWE
    to_be_removed = [first_mwe_lex]
    ref = 0
    # We set the ref variable to the position of the first lex of the
    # first MWE
    for i in sorted(savelex):
        if savelex[i] == None:
            ref = i+1
            break
    # We go through the first of the combinations. For each lex that has
    # an identical base to the first one and also a reference number
    # pointing to the first one, we mark them to be removed, keeping
    # only the first.
    for i, l in enumerate(combinations[0][1:]):
        if re.sub(':\d+','',l) == re.sub(':\d+','',first_mwe_lex) and ':' in l:
            if int(l.split(':')[-1]) == ref:
                mwe_positions.append(i+1)
                to_be_removed.append(l)
    # We go through all combinations, removing all lexes that are marked
    # for removal
    for c in combinations:
        redc = []
        remove = [r for r in to_be_removed]
        for l in c:
            if remove:
                if l == remove[0]:
                    remove.pop(0)
                else:
                    redc.append(l)
            else:
                redc.append(l)
        reduced_combinations.append(redc)
    # We then add the removed lexes to savelex
    counter = 0
    for i in sorted(savelex):
        # The first None in the savelex should correspond to the first
        # lex of the first MWE
        if not mwe_positions:
            break
        if counter == 0 and savelex[i] == None:
            savelex[i] = first_mwe_lex
            mwe_positions.pop(0)
            counter += 1
        # We remove all other lexes that are part of the first MWE from
        # savelex
        elif counter == mwe_positions[0] and savelex[i] == None:
            savelex.pop(i)
            mwe_positions.pop(0)
            counter += 1
        # Other MWEs are left alone
        elif savelex[i] == None:
            counter += 1
    return reduced_combinations, savelex


def check_mwe(sentence, mode):
    '''A function to contract Multi-Word Expressions (MWEs) in an XML
    sentence from a Korp corpus. Returns a list of the contents of each
    word's LEX tag, with two modifications: 1) If there is no LEX tag,
    it will be substituted by the word itself, and 2) Each MWE will
    only be written at the position of the first part of that MWE.
    The main heuristics are to 1) choose the longest MWEs and 2) choose
    the leftmost MWE. While this should take care of nearly all cases,
    we might update the code with a third heuristic to choose the most
    compact MWE.'''
    global sep
    # We set the separator to space if the mode is lemma, otherwise
    # to underscore
    if mode == 'lemma':
        sep = ' '
    else:
        sep = '_'
    # We make a list of lists of lexes:
    lexlists = []
    for w in sentence:
        # Sometimes there are other elements than <w> in a sentence
        # element. Whenever that is the case, we return None
        if w.tag != 'w':
            return None
        # For some reason, the parser have troubles with words
        # sometimes, setting them to None, which causes errors
        if w.text == None:
            w.text = 'noword'
        # The pipe symbol | is used as a separator in the annotation
        # lexes is a list of lexes for a given word
        lexes = [l for l in w.attrib[mode].split('|') if l]
        # We check how many MWE lexes there are for the current word
        mwes = [l for l in lexes if sep in l and not l.startswith(sep)
                and not l.startswith('http')]
        # If we find any, we remove all duplicates before adding the
        # list of lexes to the lexlist
        if len(mwes) > 0:
            if mode != 'lemma':
                lexes = join_identicals(lexes)
            lexlists.append(lexes)
        # If there are no lexes for the current word, we append the
        # word instead
        elif len(lexes) == 0:
            lexlists.append([w.text])
        # If there are lexes for the current word, but no MWE, we
        # choose the first lex
        else:
            lexlists.append(['|'.join(lexes)])

    # If there are no MWE's in the sentence, we return a list of the
    # first lex of each word. We assume that there is an MWE if any lex
    # has an underscore which is not at the beginning of the string
    if not [w.attrib[mode] for w in sentence if sep in w.attrib[mode] and not
            w.attrib[mode].startswith(sep)]:
        # We flatten the list before returning it
        lexes_out = [lex for wlexes in lexlists for lex in wlexes]
        return lexes_out

    # If we are certain of a single lex, we save it along with its
    # word's position in the sentence. The position will be needed
    # later to determine valid references among lexes. Positions
    # are here counted from zero.
    savelex = {}
    # and make a list of those we are unsure of
    uslist = []
    for i, lexes in enumerate(lexlists):
        mwes = [l for l in lexes if sep in l and not l.startswith(sep)
                and not l.startswith('http')]
        # If there is only one lex to choose and it's not part of
        # a MWE, we choose that
        # was: if len(lexes) == 1 and '_' not in lexes[0]:
        if len(lexes) == 1 and (sep not in lexes[0]
                                or lexes[0].startswith(sep)
                                or lexes[0].startswith('http')):
            savelex[i] = lexes[0]
        # In case we have an empty word tag and the lexes is empty
        elif not lexes:
            savelex[i] = ''
        # If no MWEs are found we choose the first
        elif not mwes:
            savelex[i] = '|'.join(lexes)
        # Sometimes we have one lex tagged as an MWE and only
        # that, although it doesn't match other words' lexes. This
        # probably means that a contracted form of a MWE has been used.
        # If we find an underscore we store it as None for now, unless
        # it's of a MWE that is alone, in which case we save it properly
        else:
            # We make a flat list of all lexes for all words in the
            # sentence except for the word we are working on
            all_except_current = lexlists[:i] + lexlists[i+1:]
            all_flat = [re.sub(':\d+','',i) for l
                        in all_except_current for i in l]
            # We check whether the MWE lexes for the current word matches
            # the lexes for any other words in the sentence
            identicals = False
            for l in mwes:
                if re.sub(':\d+','',l) in all_flat:
                    identicals = True
                    break
            # If we don't find a match, we save it
            # Since the first item might be a wrongly added MWE-word, we
            # choose the first without underscores if that exists
            if identicals == False:
                non_mwes = [l for l in lexes if l not in mwes]
                if non_mwes:
                    savelex[i] = non_mwes[0]
                else:
                    savelex[i] = lexes[0]
            # If we find a match, we have a proper MWE that neeeds to be
            # contracted. We save it as None and add it to the list of
            # unsure lexes
            else:
                savelex[i] = None
                uslist.append(lexes)

    # In case our uncertain list is empty, we return our saved items
    if not uslist:
        return [savelex[i] for i in sorted(savelex)]
    # In case we have a big uslist, the number of combinations might
    # become enormous. We should preferably pre-process the uslist
    # whenever that happens, but for now, we'll simply set 33 as a
    # cutoff. If the flat uslist is bigger than that, we choose the
    # first possible combination. We write the uslist to a log file
    # to make it easier to handle it properly later.

    # Instead of flattening the list, we calculate the product
    # beforehand:
    comblength = 1
    uslengths = [len(l) for l in uslist]
    for i in uslengths:
        comblength *= i

    if comblength > 500000:
        print("Too many combinations!: %s" % comblength)
        print("Skipping")
        with open('flatuslog.txt', 'a+') as logfile:
            logfile.write("------------------")
            for l in uslist:
                lstring = ' '.join(l)
                logfile.write(lstring + '\n')
        return None

    # We generate all combinations of the unsure ones
    combinations = it.product(*uslist)
    # We convert the generator into a list
    combinations = [c for c in combinations]
    # Then we remove all combinations that are referentially invalid
    valid_combinations = get_valid_combinations(combinations, savelex)
    # In some cases, Korp's annotation doesn't provide any valid
    # combinations. In this case, we choose either the first
    # combination with an MWE for the first lex, if it exists, or, if
    # it doesn't, the first combination there is
    if not valid_combinations:
        for c in combinations:
            if sep in c[0] and not c[0].startswith(sep):
                return combination_to_out(c, savelex)
        return combination_to_out(combinations[0], savelex)

    # In case the list of combinations is really large, we delete it
    del combinations

    # We remove all combinations that are identical to another
    # combination except for the SALDO numbers being different,
    # keeping only the first
    valid_combinations = remove_identicals(valid_combinations)

    # At some point I get empty combinations. I need to find out what causes
    # that. For the time being, we'll just remove them
    # The following four lines should  be removed after one more round of testing
    valid_combinations = [c for c in valid_combinations if c]
    unsures = [i for i in sorted(savelex) if savelex[i] == None]
    if not unsures:
        return [savelex[i] for i in sorted(savelex)]

    # Do we have only one valid combination? Choose that!
    if len(valid_combinations) == 1:
        return combination_to_out(valid_combinations[0], savelex)
    # Do we have the option to use all words in one MWE? Choose that!
    for c in valid_combinations:
        # We check that the length of the MWE is equal to the number
        # of lexes in the combination
        if not c[0].startswith(sep) and len(c[0].split(sep)) == len(c):
            # We check whether all words in the combination are part of
            # the same MWE
            sameas = [l for l in c if
                      re.sub(':\d+','',l) == re.sub(':\d+','',c[0])]
            if len(sameas) == len(c):
                return combination_to_out(c, savelex)
    # We reduce the list of combinations to the one(s) with the most
    # words used in MWEs
    max_combinations = get_max_mwe_words(valid_combinations)
    # We also check whether we are finished and return if we are
    if len(max_combinations) == 1:
        return combination_to_out(max_combinations[0], savelex)

    # Here we start the following process
    # 1) Save and remove the leading lexes from combinations if
    # they are not part of a MWE
    # 2) Remove combinations that are not among those with
    # the leftmost of the longest MWE
    # 3) Save the first MWE
    # Repeat if we have managed to reduce the number of combinations
    last_length = len(max_combinations) + 1
    while len(max_combinations) < last_length:
        if len(max_combinations) == 1:
            return combination_to_out(max_combinations[0], savelex)
        elif len(max_combinations) == 0:
            return combination_to_out([], savelex)
        last_length = len(max_combinations)
        # If all combinations start with lexes that are not part of a
        # MWE, we move them to savelex.
        max_combinations, savelex = remove_leading_non_mwes(max_combinations,
                                                            savelex)
        # Now we know that the first lex in max_combinations is part of
        # a MWE. We remove all combinations where the first MWE is
        # shorter than the longest possible.
        max_combinations = get_best_leftmost(max_combinations)
        # Assuming that the first MWE is the same for all combinations,
        # we move that MWE to savelex
        max_combinations, savelex = save_first_mwe(max_combinations, savelex)

    # When we no longer are able to reduce the number of combinations,
    # we repeat steps 1 and 3 as long as it reduces the first
    # combination
    last_length = len(max_combinations[0]) + 1
    while max_combinations and len(max_combinations[0]) < last_length:
        if not max_combinations[0]:
            return combination_to_out([], savelex)
        last_length = len(max_combinations[0])
        max_combinations, savelex = remove_leading_non_mwes(max_combinations, savelex)
        max_combinations, savelex = save_first_mwe(max_combinations, savelex)

    # If at this point we haven't yet found a winning combination, we
    # choose the first available. It might also be that we have emptied
    # the list of combinations, in which case we use an empty list.
    if len(max_combinations) == 0:
        return combination_to_out([], savelex)
    elif len(max_combinations) >= 1:
        return combination_to_out(max_combinations[0], savelex)



if __name__ == '__main__':
    print("You probably want to use bw_extract.py instead of this one")
