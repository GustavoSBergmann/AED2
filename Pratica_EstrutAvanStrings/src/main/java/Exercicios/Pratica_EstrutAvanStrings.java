package Exercicios;

import org.apache.commons.collections4.trie.PatriciaTrie;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.SortedMap;

public class Pratica_EstrutAvanStrings {

    private final PatriciaTrie<Boolean> trie = new PatriciaTrie<>();

    public void popularVocabularioExemplo() {
        String[] vocabulario = {"pato", "grama", "grana", "pa", "grampo", "paz", "gol"};
        for (String palavra : vocabulario) {
            trie.put(palavra, Boolean.TRUE);
        }
    }

    // EXERCÍCIO 1
    public boolean buscarPalavra(String palavra) {
        return trie.containsKey(palavra);
    }

    // EXERCÍCIO 2
    public List<String> buscarPorPrefixo(String prefixo) {
        SortedMap<String, Boolean> submapa = trie.prefixMap(prefixo);
        return new ArrayList<>(submapa.keySet());
    }

    public static void main(String[] args) {
        Pratica_EstrutAvanStrings app = new Pratica_EstrutAvanStrings();
        app.popularVocabularioExemplo();

        System.out.println("buscarPalavra(grama) = " + app.buscarPalavra("grama"));
        System.out.println("buscarPalavra(gra)   = " + app.buscarPalavra("gra"));
        System.out.println("buscarPalavra(gol)   = " + app.buscarPalavra("gol"));
        System.out.println("buscarPalavra(golfo) = " + app.buscarPalavra("golfo"));

        System.out.println("buscarPorPrefixo(gra) = " + app.buscarPorPrefixo("gra"));
        System.out.println("buscarPorPrefixo(pa)  = " + app.buscarPorPrefixo("pa"));
    }
}
